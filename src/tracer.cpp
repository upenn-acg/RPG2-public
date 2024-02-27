#include "tracer.hpp"

using namespace std;

void signal_handler(int sig){
    printf("Caught signal %d\n", sig);
}


int main(){
   // TCP resources initialization
   // TCP connections is used for getting the 
   // starting address of the function in 
   // ld_preload
   pg2_env pg2_environ;
   struct sockaddr_in servaddr;
   createTCPsocket(pg2_environ.listen_fd, servaddr);

   // spawn target process
   pid_t target_PID = fork();
   if (target_PID == 0){
      // child - target server process
      createTargetProcess(&pg2_environ);
      printf("[tracer] target server process creation fails\n");
   }
   else {
      // create the signal handler in order to capture 
      // SIGKILL from child process
      signal(SIGUSR1,signal_handler);
      // parent - tracer process
      // wait for child to send the addr of library 
      // function back via TCP connection 
      void* lib_addr = get_lib_addr(pg2_environ.listen_fd);		

      // create a thread to send the path that stores
      // inject_prefetch.data & moved_functions &
      // unmoved functions
      thread t = thread(send_data_path, &pg2_environ);
      
      wait_for_starting_signal();

      double original_IPC;
      uint64_t BOLT_starting_addr=0;
      uint64_t original_starting_addr=0;
      long moved_size = 0;
      long original_size = 0;
      int initial_prefetch_dist = generate_random_number(6,100);
      int num_pd_edit = 3;
      map<uint64_t, uint64_t> reversed_bat;
      // get all functions that have location changed		
      unordered_map<long, func_info> func_with_addr = get_func_with_original_addr(&pg2_environ);

      map<long, func_info> func_heap = change_func_to_heap(func_with_addr);
      map<long, vector<vector<uint8_t>>> prefetch_addr_with_machine_codes; 
      unordered_map<long, func_info> bolted_func; 
      vector<pair<int, int>> prefetch_dist_locations;
      vector<float> pd_edit_time;      
      float bolt_time, insertion_time;

      #ifdef TIME_MEASUREMENT
      auto begin_all = std::chrono::high_resolution_clock::now();
      #endif


      // in the first round of execution                
      // (1) first use BOLT to produce the optimized    
      //     binary that contains prefetch instruction  
      // (2) extract the function that is moved by BOLT 
      // (3) inject the moved function to the target    
      //     process                                    
      inject_BOLTed_function(bolted_func, reversed_bat,
                             BOLT_starting_addr,
                             original_starting_addr,
                             original_size,
                             moved_size,
                             original_IPC, pg2_environ,
                             target_PID, lib_addr, 
                             bolt_time, insertion_time);

      // in the second round of execution, pg2                               
      // (1) first extracts prefetch in the functions that 
      //     are moved by BOLT 
      // (2) then changes the prefetch distance to be 5                      
      // (3) inject the new prefetch distance to the target 
      //     process          
      initialize_prefetch_dist(pg2_environ, bolted_func,
                               lib_addr, target_PID,
                               prefetch_addr_with_machine_codes, 
                               initial_prefetch_dist);

      int optimal_pref_dist = 5;
      double optimal_IPC = 0;
      bool should_prefetch_right = false;
      bool should_prefetch_left = false;
      vector<IPC_info> right_info;
      vector<IPC_info> left_info;
      // in the 3rd, 4th, 5th ... rounds of execution, 
      // pg2 only changes the prefetch distance        
      // and then inject the new prefetch distance to  
      // the target process                            

      test_prefetch_directions(pg2_environ, lib_addr, target_PID, 
                               optimal_pref_dist, optimal_IPC, 
                               prefetch_addr_with_machine_codes,
                               initial_prefetch_dist,
                               right_info, left_info,
                               should_prefetch_right, should_prefetch_left,
                               pd_edit_time);


      test_different_prefetch_dist(pg2_environ, lib_addr, target_PID,
                                   optimal_pref_dist, optimal_IPC,
                                   prefetch_addr_with_machine_codes, 
                                   initial_prefetch_dist,
                                   should_prefetch_right, should_prefetch_left,
                                   right_info, left_info, 
                                   num_pd_edit, pd_edit_time);


      decide_prefetch_distance_or_revert(pg2_environ, lib_addr,
                                         reversed_bat, target_PID,
                                         original_starting_addr,
                                         BOLT_starting_addr,
                                         optimal_pref_dist,
                                         optimal_IPC, original_IPC,
                                         prefetch_addr_with_machine_codes);



      #ifdef TIME_MEASUREMENT
      auto end_all = std::chrono::high_resolution_clock::now();
      auto elapsed_all = std::chrono::duration_cast<std::chrono::nanoseconds>(end_all - begin_all);
      printf("[tracer] pg2 overall execution time is %f seconds \n", elapsed_all.count() * 1e-9);
      #endif

      float sum_of_pd_edit_time = 0.0;
      for (unsigned i=0; i<pd_edit_time.size(); i++){
         sum_of_pd_edit_time += pd_edit_time[i];
      }
      printf("[tracer] prefetch insertion time: %f seconds\n", insertion_time);
      printf("[tracer] BOLTed binary producing time: %f seconds\n", bolt_time);
      printf("[tracer] average time on prefetch distance editing: %f seconds\n", sum_of_pd_edit_time/pd_edit_time.size());
      printf("[tracer] number of trials for editing prefetch distance: %d\n", num_pd_edit); 
      printf("[tracer] optimal IPC=%lf\n", optimal_IPC);
      printf("[tracer] optimal pref_dist = %d\n", optimal_pref_dist);
      #ifdef CLEAN_UP
      #ifndef DEBUG_INFO
      clean_up(&pg2_environ);
      #endif
      #endif

      t.join();    
   }
   exit(0);
}


void inject_BOLTed_function(unordered_map<long, func_info>& bolted_func,
                            map<uint64_t, uint64_t>& reversed_bat,
                            uint64_t &BOLT_starting_addr,
                            uint64_t &original_starting_addr,
                            long &original_size,
                            long &moved_size,
                            double &original_IPC,
                            pg2_env &pg2_environ,
                            pid_t target_PID,
                            void* lib_addr,
                            float& bolt_time,
                            float& insertion_time){

   // run perf stat to get the current IPC
   #ifdef TIME_MEASUREMENT
   auto begin_perf_stat = std::chrono::high_resolution_clock::now();
   #endif

   original_IPC = run_perf_stat(&pg2_environ, target_PID); 

   #ifdef TIME_MEASUREMENT
   auto end_perf_stat = std::chrono::high_resolution_clock::now();
   auto elapsed_perf_stat = std::chrono::duration_cast<std::chrono::nanoseconds>(end_perf_stat - begin_perf_stat);
   printf("[tracer][time] perf stat took %f seconds to execute \n", elapsed_perf_stat.count() * 1e-9);
   #endif

   run_perf_record(target_PID, &pg2_environ);
   string top_llc_miss_func = run_perf_report(&pg2_environ);
   run_perf_script(top_llc_miss_func, &pg2_environ);
   //string top_llc_miss_instr = run_perf_script(top_llc_miss_func, &pg2_environ);
   //write_TopLLCMiss_info_to_file(top_llc_miss_func, top_llc_miss_instr, &pg2_environ);
   test_prefetchable_location(&pg2_environ);
   bolted_func = run_llvmbolt(&pg2_environ, bolt_time);
   reversed_bat = run_bat_dump(&pg2_environ);

   extract_call_sites(bolted_func, &pg2_environ);

   // get the information from the BOLTed binary 
   // in order to extract the delta between the 
   // original and BOLTed binary 
   BOLT_starting_addr = bolted_func.begin()->second.moved_addr;
   original_starting_addr = bolted_func.begin()->second.original_addr;
   original_size = bolted_func.begin()->second.original_size;
   moved_size = bolted_func.begin()->second.moved_size;
   vector<long> addr_bolted_func = get_moved_addr_to_array(bolted_func);
   unordered_map<long, func_info> unmoved_func = get_unmoved_func(&pg2_environ, bolted_func);
   vector<long> addr_unmoved_func = get_keys_to_array(unmoved_func);

   // in the first round of execution, pg2 injects 
   // (1) functions that are moved by BOLT
   // (2) functions that are not moved by BOLT
   // (3) v-table
   write_functions ( pg2_environ.bolt_opt_bin_path.c_str(),
                     pg2_environ.bolted_function_bin.c_str(),
                     addr_bolted_func.data(),
                     addr_bolted_func.size());

   write_functions ( pg2_environ.bolt_opt_bin_path.c_str(), 
                     pg2_environ.unmoved_func_bin.c_str(), 
                     addr_unmoved_func.data(), 
                     addr_unmoved_func.size());

   write_vtable ( pg2_environ.bolt_opt_bin_path.c_str(),
                  pg2_environ.v_table_bin.c_str() );
        

   // measure the ptrace pause time
   auto begin = std::chrono::high_resolution_clock::now();

   // to pause all running threads of the target process
   // and then get the PIDs(tid) of these threads
   vector<pid_t> tids = pause_and_get_tids(target_PID);

   // unwind call stack and get the functions
   // in the call stacks of each threads
   vector<unw_word_t> call_stack_ips = unwind_call_stack(tids);
//         unordered_map<long, func_info> func_in_call_stack =  get_func_in_call_stack(call_stack_ips, func_heap);

	
   // change the IP of the target process to be 
   // the starting address of our library code 
   // then make the target process to execute 
   // the lib code to insert machine code
   struct user_regs_struct regs, old_regs;
   struct user_fpregs_struct fregs;
   for (unsigned j=0; j<tids.size(); j++){
      if(!ptrace_single_step(tids[j], lib_addr, regs, old_regs, fregs)){
         continue;
      }
      old_regs.rip = address_translation_orig2bolt(old_regs.rip, 
                                                  original_starting_addr, 
                                                  BOLT_starting_addr, 
                                                  reversed_bat);

      ptrace_cont(tids[j], regs, old_regs, fregs);
      break;			
   }

   #ifdef DEBUG	
   // deliver a SIGSTOP signal to target process. 
   // before resume the target process, so that 
   // we can attach GDB to target process later on.
   for (unsigned j=0; j<tids.size(); j++){
      int rc = syscall(SYS_tgkill, tids[0], tids[j], SIGSTOP);	
   }
   #endif

   // ptrace detach all threads of the target process
   for (unsigned j=0; j<tids.size(); j++){
      ptrace(PTRACE_DETACH, tids[j], NULL, NULL);	
   }

   auto end = std::chrono::high_resolution_clock::now();
   auto elapsed = std::chrono::duration_cast<std::chrono::nanoseconds>(end - begin);
   #ifdef TIME_MEASUREMENT
   printf("[tracer][time] machine code insertion took %f seconds to execute \n", elapsed.count() * 1e-9);
   #endif
   insertion_time = elapsed.count() * 1e-9; 


   #ifdef DEBUG_INFO  
   printf("[tracer][OK] code replacement done!\n");
   #endif

   #ifdef DEBUG
   while(true);
   #endif
}



void initialize_prefetch_dist(pg2_env &pg2_environ,
                              unordered_map<long, func_info>& bolted_func,
                              void* lib_addr,
                              pid_t target_PID,
                              map<long, vector<vector<uint8_t>>>& prefetch_addr_with_machine_codes,
                              int initial_prefetch_dist){ 

  prefetch_addr_with_machine_codes 
               = extract_prefetch_insn(&pg2_environ, bolted_func);
  change_prefetch_dist_lt(&pg2_environ, initial_prefetch_dist, prefetch_addr_with_machine_codes);
         
  // to pause all running threads of the target process
  // and then get the PIDs(tid) of these threads
  vector<pid_t> tids = pause_and_get_tids(target_PID);

  // unwind call stack and get the functions
  // in the call stacks of each threads
  vector<unw_word_t> call_stack_ips = unwind_call_stack(tids);
//         unordered_map<long, func_info> func_in_call_stack =  get_func_in_call_stack(call_stack_ips, func_heap);

  // change the IP of the target process to be 
  // the starting address of our library code 
  // then make the target process to execute 
  // the lib code to insert machine code
  struct user_regs_struct regs, old_regs;
  struct user_fpregs_struct fregs;

  for (unsigned j=0; j<tids.size(); j++){
     if(!ptrace_single_step(tids[j], lib_addr, regs, old_regs, fregs)){
        continue;
     }
     ptrace_cont(tids[j], regs, old_regs, fregs);
     break;			
  }

  #ifdef DEBUG	
  // deliver a SIGSTOP signal to target process. 
  // before resume the target process, so that 
  // we can attach GDB to target process later on.
  for (unsigned j=0; j<tids.size(); j++){
     int rc = syscall(SYS_tgkill, tids[0], tids[j], SIGSTOP);	
  }
  #endif

  // ptrace detach all threads of the target process
  for (unsigned j=0; j<tids.size(); j++){
     ptrace(PTRACE_DETACH, tids[j], NULL, NULL);	
  }

  #ifdef DEBUG_INFO  
  printf("[tracer][OK] code replacement done!\n");
  #endif

  #ifdef DEBUG
  while(true);
  #endif  
}






void edit_prefetch_dist(pg2_env &pg2_environ,
                        void* lib_addr,
                        pid_t target_PID,
                        int pref_dist,
                        map<long, vector<vector<uint8_t>>>& prefetch_addr_with_machine_codes,
                        float& pd_edit_time){

   change_prefetch_dist_lt(&pg2_environ, pref_dist, prefetch_addr_with_machine_codes);
         
   // measure the ptrace pause time
   auto begin = std::chrono::high_resolution_clock::now();

   // to pause all running threads of the target process
   // and then get the PIDs(tid) of these threads
   vector<pid_t> tids = pause_and_get_tids(target_PID);

   // unwind call stack and get the functions
   // in the call stacks of each threads
   vector<unw_word_t> call_stack_ips = unwind_call_stack(tids);
// unordered_map<long, func_info> func_in_call_stack =  get_func_in_call_stack(call_stack_ips, func_heap);

	
   // change the IP of the target process to be 
   // the starting address of our library code 
   // then make the target process to execute 
   // the lib code to insert machine code
   struct user_regs_struct regs, old_regs;
   struct user_fpregs_struct fregs;


   for (unsigned j=0; j<tids.size(); j++){
      if(!ptrace_single_step(tids[j], lib_addr, regs, old_regs, fregs)){
         continue;
      }
      ptrace_cont(tids[j], regs, old_regs, fregs);
      break;			
   }

   #ifdef DEBUG	
   // deliver a SIGSTOP signal to target process. 
   // before resume the target process, so that 
   // we can attach GDB to target process later on.
   for (unsigned j=0; j<tids.size(); j++){
      int rc = syscall(SYS_tgkill, tids[0], tids[j], SIGSTOP);	
   }
   #endif

   // ptrace detach all threads of the target process
   for (unsigned j=0; j<tids.size(); j++){
      ptrace(PTRACE_DETACH, tids[j], NULL, NULL);	
   }

   auto end = std::chrono::high_resolution_clock::now();
   auto elapsed = std::chrono::duration_cast<std::chrono::nanoseconds>(end - begin);
   #ifdef TIME_MEASUREMENT
   printf("[tracer][time] machine code insertion took %f seconds to execute \n", elapsed.count() * 1e-9);
   #endif
   pd_edit_time = elapsed.count() * 1e-9; 

   #ifdef DEBUG_INFO  
   printf("[tracer][OK] code replacement done!\n");
   #endif

   #ifdef DEBUG
   while(true);
   #endif

}







void test_different_prefetch_dist(pg2_env &pg2_environ,
                                  void* lib_addr,
                                  pid_t target_PID,
                                  int &optimal_pref_dist,
                                  double &optimal_IPC,
                                  map<long, vector<vector<uint8_t>>>& prefetch_addr_with_machine_codes,
                                  int initial_prefetch_dist, 
                                  bool should_prefetch_right,
                                  bool should_prefetch_left,
                                  vector<IPC_info> right_info,
                                  vector<IPC_info> left_info,
                                  int& num_pd_edit,
                                  vector<float>& pd_edit_time ){

   int current_pref_dist = initial_prefetch_dist+15;
   vector<IPC_info> IPC_prefDist = right_info;
//   IPC_info first_info(0, initial_prefetch_dist);
//   IPC_prefDist.push_back(first_info);

   if ((!should_prefetch_right) && (!should_prefetch_left)){
      change_prefetch_dist_lt(&pg2_environ, initial_prefetch_dist, prefetch_addr_with_machine_codes);

      // to pause all running threads of the target process
      // and then get the PIDs(tid) of these threads
      vector<pid_t> tids = pause_and_get_tids(target_PID);

      // unwind call stack and get the functions
      // in the call stacks of each threads
      vector<unw_word_t> call_stack_ips = unwind_call_stack(tids);
//    unordered_map<long, func_info> func_in_call_stack =  get_func_in_call_stack(call_stack_ips, func_heap);

	
      // change the IP of the target process to be 
      // the starting address of our library code 
      // then make the target process to execute 
      // the lib code to insert machine code
      struct user_regs_struct regs, old_regs;
      struct user_fpregs_struct fregs;

      for (unsigned j=0; j<tids.size(); j++){
         if(!ptrace_single_step(tids[j], lib_addr, regs, old_regs, fregs)){
            continue;
         }
         ptrace_cont(tids[j], regs, old_regs, fregs);
         break;			
      }

      // ptrace detach all threads of the target process
      for (unsigned j=0; j<tids.size(); j++){
         ptrace(PTRACE_DETACH, tids[j], NULL, NULL);	
      }

      optimal_IPC = run_perf_stat(&pg2_environ, target_PID); 
      optimal_pref_dist = initial_prefetch_dist;

   }


   float time;
   if (should_prefetch_right){
      edit_prefetch_dist (pg2_environ, lib_addr, target_PID, current_pref_dist,
                          prefetch_addr_with_machine_codes, time);
      IPC_info new_info(0, current_pref_dist);
      IPC_prefDist.push_back(new_info);

      for (int i=0; ; i++){
         // run perf stat to get the current IPC
         #ifdef TIME_MEASUREMENT
         auto begin_perf_stat = std::chrono::high_resolution_clock::now();
         #endif

         num_pd_edit++;

         double current_IPC = run_perf_stat(&pg2_environ, target_PID); 

         #ifdef TIME_MEASUREMENT
         auto end_perf_stat = std::chrono::high_resolution_clock::now();
         auto elapsed_perf_stat = std::chrono::duration_cast<std::chrono::nanoseconds>(end_perf_stat - begin_perf_stat);
         printf("[tracer][time] perf stat took %f seconds to execute \n", elapsed_perf_stat.count() * 1e-9);
         #endif

         IPC_prefDist.back().IPC = current_IPC;
         if (should_stop(IPC_prefDist)) break;
         if (current_IPC > optimal_IPC) {
            optimal_IPC = current_IPC;
            optimal_pref_dist = current_pref_dist;
         }
         compute_new_prefetch_dist(IPC_prefDist); 
         current_pref_dist = IPC_prefDist.back().prefetch_distance;
         edit_prefetch_dist (pg2_environ, lib_addr, target_PID, current_pref_dist,
                             prefetch_addr_with_machine_codes, time);
         pd_edit_time.push_back(time);
      }
   }

   current_pref_dist = initial_prefetch_dist - 15 > 0? initial_prefetch_dist-15 : 1;
   vector<IPC_info> IPC_prefDist_left = left_info;
//   IPC_info first_info_left(0, initial_prefetch_dist);
//   IPC_prefDist_left.push_back(first_info_left);

   if (should_prefetch_left){
      edit_prefetch_dist (pg2_environ, lib_addr, target_PID, current_pref_dist,
                          prefetch_addr_with_machine_codes, time);
      IPC_info new_info(0, current_pref_dist);
      IPC_prefDist.push_back(new_info);

      for (int i=0; ; i++){
         num_pd_edit++;
         // run perf stat to get the current IPC
         #ifdef TIME_MEASUREMENT
         auto begin_perf_stat = std::chrono::high_resolution_clock::now();
         #endif

         double current_IPC = run_perf_stat(&pg2_environ, target_PID); 

         #ifdef TIME_MEASUREMENT
         auto end_perf_stat = std::chrono::high_resolution_clock::now();
         auto elapsed_perf_stat = std::chrono::duration_cast<std::chrono::nanoseconds>(end_perf_stat - begin_perf_stat);
         printf("[tracer][time] perf stat took %f seconds to execute \n", elapsed_perf_stat.count() * 1e-9);
         #endif

         IPC_prefDist_left.back().IPC = current_IPC;
         if (should_stop_left(IPC_prefDist_left)) break;
         if (current_IPC > optimal_IPC) {
            optimal_IPC = current_IPC;
            optimal_pref_dist = current_pref_dist;
         }
         compute_new_prefetch_dist_left(IPC_prefDist_left); 
         current_pref_dist = IPC_prefDist_left.back().prefetch_distance;
         edit_prefetch_dist (pg2_environ, lib_addr, target_PID, current_pref_dist,
                             prefetch_addr_with_machine_codes, time);
         pd_edit_time.push_back(time);
      }
   }
}






void test_prefetch_directions(pg2_env &pg2_environ,
                              void* lib_addr,
                              pid_t target_PID,
                              int &optimal_pref_dist,
                              double &optimal_IPC,
                              map<long, vector<vector<uint8_t>>>& prefetch_addr_with_machine_codes,
                              int initial_prefetch_dist,
                              vector<IPC_info>& IPC_prefDist_right,
                              vector<IPC_info>& IPC_prefDist_left,
                              bool& should_test_right,
                              bool& should_test_left,
                              vector<float>& pd_edit_time){

   float time;

   edit_prefetch_dist (pg2_environ, lib_addr, target_PID, initial_prefetch_dist,
                       prefetch_addr_with_machine_codes, time);
   pd_edit_time.push_back(time);

   double initial_IPC = run_perf_stat(&pg2_environ, target_PID); 

   edit_prefetch_dist (pg2_environ, lib_addr, target_PID, initial_prefetch_dist-5,
                       prefetch_addr_with_machine_codes, time);
   pd_edit_time.push_back(time);

   double IPC_left = run_perf_stat(&pg2_environ, target_PID); 

   edit_prefetch_dist (pg2_environ, lib_addr, target_PID, initial_prefetch_dist+5,
                       prefetch_addr_with_machine_codes, time);
   pd_edit_time.push_back(time);

   double IPC_right = run_perf_stat(&pg2_environ, target_PID); 

   if (IPC_right +0.05 > initial_IPC) should_test_right = true;
   if (IPC_left + 0.05 > initial_IPC) should_test_left = true; 

   IPC_info orig(initial_IPC, initial_prefetch_dist);
   IPC_info right(IPC_right, initial_prefetch_dist+5);
   IPC_info left(IPC_left, initial_prefetch_dist-5);

   IPC_prefDist_left.push_back(orig);
   IPC_prefDist_left.push_back(left); 

   IPC_prefDist_right.push_back(orig);
   IPC_prefDist_right.push_back(right); 
}






void decide_prefetch_distance_or_revert(pg2_env &pg2_environ,
                                       void* lib_addr,
                                       map<uint64_t, uint64_t>& reversed_bat,
                                       pid_t target_PID,
                                       uint64_t original_starting_addr,
                                       uint64_t BOLT_starting_addr,
                                       int &optimal_pref_dist,
                                       double optimal_IPC,
                                       double original_IPC,
                                       map<long, vector<vector<uint8_t>>>& prefetch_addr_with_machine_codes){

   if (optimal_IPC < original_IPC) {
      map<uint64_t, uint64_t> bat = gen_bat_from_reversedBat(reversed_bat);
      printf("[tracer] need to go back to the original\n");
      // to pause all running threads of the target process
      // and then get the PIDs(tid) of these threads
      vector<pid_t> tids = pause_and_get_tids(target_PID);

      // unwind call stack and get the functions
      // in the call stacks of each threads
      vector<unw_word_t> call_stack_ips = unwind_call_stack(tids);
      
      for (unsigned i=0; i<tids.size(); i++){
         struct user_regs_struct regs;
         ptrace(PTRACE_GETREGS, tids[i], NULL, &regs);
         printf("[tracer] current rip=0x%llx\n", regs.rip);
         if (regs.rip > BOLT_starting_addr){
            if(!ptrace_single_step0(tids[i], regs)){
               continue;
            }
            while (bat.find(regs.rip - BOLT_starting_addr)==bat.end()){
               ptrace_single_step0(tids[i], regs);
            }
            regs.rip = address_translation_bolt2orig(regs.rip, original_starting_addr, BOLT_starting_addr, bat);
            ptrace(PTRACE_SETREGS, tids[i], NULL, &regs);
            printf("[tracer] revert back to rip=0x%llx\n", regs.rip);
            break;			
         }
      }
         

      #ifdef DEBUG	
      // deliver a SIGSTOP signal to target process. 
      // before resume the target process, so that 
      // we can attach GDB to target process later on.
      for (unsigned i=0; i<tids.size(); i++){
         int rc = syscall(SYS_tgkill, tids[0], tids[i], SIGSTOP);	
      }
      #endif

      // ptrace detach all threads of the
      // target process
      for (unsigned i=0; i<tids.size(); i++){
         ptrace(PTRACE_DETACH, tids[i], NULL, NULL);	
      }

   }
   else{
      change_prefetch_dist_lt(&pg2_environ, optimal_pref_dist, prefetch_addr_with_machine_codes);

      // to pause all running threads of the target process
      // and then get the PIDs(tid) of these threads
      vector<pid_t> tids = pause_and_get_tids(target_PID);
      // unwind call stack and get the functions
      // in the call stacks of each threads
      vector<unw_word_t> call_stack_ips = unwind_call_stack(tids);
      // change the IP of the target process to be 
      // the starting address of our library code 
      // then make the target process to execute 
      // the lib code to insert machine code
      struct user_regs_struct regs, old_regs;
      struct user_fpregs_struct fregs;
      for (unsigned i=0; i<tids.size(); i++){
         if(!ptrace_single_step(tids[i], lib_addr, regs, old_regs, fregs)){
            continue;
         }
         ptrace_cont(tids[i], regs, old_regs, fregs);
         break;			
      }

      #ifdef DEBUG	
      // deliver a SIGSTOP signal to target process. 
      // before resume the target process, so that 
      // we can attach GDB to target process later on.
      for (unsigned i=0; i<tids.size(); i++){
         int rc = syscall(SYS_tgkill, tids[0], tids[i], SIGSTOP);	
      }
      #endif
      // ptrace detach all threads of the
      // target process
      for (unsigned i=0; i<tids.size(); i++){
         ptrace(PTRACE_DETACH, tids[i], NULL, NULL);	
      }
   }
}


int generate_random_number(int min, int max){
  std::random_device dev;
  std::mt19937 rng(dev());
  std::uniform_int_distribution<std::mt19937::result_type> dist(min, max); // distribution in range [1, 6]
  return dist(rng);     
}
