#include "bolt.hpp"

using namespace std;



void test_prefetchable_location(const pg2_env* pg2_environ){ 
   string command = ""+pg2_environ->llvmbolt_path+" --enable-bat "+
                    "--inject-prefetch --test-prefetchable --prefetch-location-file="+
                    pg2_environ->tmp_data_path+"prefetch_loc.txt "+
                    pg2_environ->target_bin_path + 
                    " -o "+
                    pg2_environ->bolt_opt_bin_path;
   char* command_cstr = new char[command.length()+1];
   strcpy(command_cstr, command.c_str()); 
   if (system(command_cstr)!=0) printf("[tracer] error in %s\n",__FUNCTION__);
   free(command_cstr);


   ifstream infile(""+pg2_environ->tmp_data_path+"prefetch_loc.txt");
   string line;
   getline(infile, line);
   if (line.empty()){
      printf("[tracer][error] prefetch_loc.txt is empty. This may be because BOLT cannot find a prefetchable location\n");
      exit(1);
   }
}



unordered_map<long, func_info> run_llvmbolt(const pg2_env* pg2_environ, float& bolt_time){
   auto begin = std::chrono::high_resolution_clock::now();

   FILE *fp1;
   char path1[3000];
   string command = ""+pg2_environ->llvmbolt_path+" --enable-bat "+
                    "--inject-prefetch --prefetch-location-file="+
                    pg2_environ->tmp_data_path+"prefetch_loc.txt "+
                    pg2_environ->target_bin_path + 
                    " -o " +
                    pg2_environ->bolt_opt_bin_path;
   char* command_cstr = new char[command.length()+1];
   strcpy(command_cstr, command.c_str()); 
   fp1 = popen(command_cstr, "r");
   free(command_cstr);

   if (fp1 == NULL){
      printf("Failed to run llvm-bolt command\n" );
      exit(-1);
   }

   // collect the bolted functions 
   // from BOLT's output
   // also collect the prefetch insertion info
   // from BOLT's output
   unordered_map<long, func_info> changed_functions;
   while (fgets(path1, sizeof(path1), fp1) != NULL) {
      string line(path1);
      vector<string> words = split_line(line);
      if (words.size()>1){
         if(words[0]=="@@@@"){
            func_info new_func;
            new_func.func_name = words[1];
            new_func.orig_addr_str = words[2];
            new_func.moved_addr_str = words[3];
            new_func.original_addr = convert_str_2_long(words[2]);
            new_func.moved_addr = convert_str_2_long(words[3]);
            new_func.original_size = convert_str_2_long(words[4]);
            new_func.moved_size = convert_str_2_long(words[5]);
            for (unsigned i=6; i<words.size(); i=i+2){
              int first_num =  convert_str_2_int(words[i]);
              int second_num =  convert_str_2_int(words[i+1]);
              new_func.prefetch_locations.push_back(make_pair(first_num, second_num));   
            }
            changed_functions[convert_str_2_long(words[2])] = new_func;
         }
      }
   }
		
   printf("[tracer] %ld functions was moved (functions reordered) by BOLT\n", changed_functions.size());
   fclose(fp1);

   auto end = std::chrono::high_resolution_clock::now();
   auto elapsed = std::chrono::duration_cast<std::chrono::nanoseconds>(end - begin);

   #ifdef TIME_MEASUREMENT
   printf("[tracer][time] llvm-bolt took %f seconds to execute \n", elapsed.count() * 1e-9);
   #endif

   bolt_time = elapsed.count() * 1e-9;

   return changed_functions;
}






map<uint64_t, uint64_t> run_bat_dump(const pg2_env* pg2_environ){
   #ifdef TIME_MEASUREMENT
   auto begin = std::chrono::high_resolution_clock::now();
   #endif

   FILE *fp1;
   char path1[3000];
   string command = ""+pg2_environ->bat_dump_path+" --dump-all "+
                    pg2_environ->bolt_opt_bin_path;
   char* command_cstr = new char[command.length()+1];
   strcpy(command_cstr, command.c_str()); 
   fp1 = popen(command_cstr, "r");
   free(command_cstr);

   if (fp1 == NULL){
      printf("[tracer][error] Failed to run bat-dump command\n" );
      exit(-1);
   }

   // collect the bolted function name 
   // from BOLT's output
   map<uint64_t, uint64_t> reversed_BAT;
   while (fgets(path1, sizeof(path1), fp1) != NULL) {
      string line(path1);
      vector<string> words = split_line(line);
      if ((words.size()>2) &&(words[1]=="->")){   
         string BOLTed_offset_str = words[0].substr(2, words[0].size()-2);
         string orig_offset_str = words[2].substr(2, words[2].size()-2);
         uint64_t BOLTed_offset = (uint64_t) convert_str_2_long(BOLTed_offset_str);
         uint64_t orig_offset = (uint64_t) convert_str_2_long(orig_offset_str);
         reversed_BAT.insert(make_pair(orig_offset, BOLTed_offset));
      }
   }

   fclose(fp1);

   #ifdef TIME_MEASUREMENT
   auto end = std::chrono::high_resolution_clock::now();
   auto elapsed = std::chrono::duration_cast<std::chrono::nanoseconds>(end - begin);
   printf("[tracer][time] bat-dump took %f seconds to execute \n", elapsed.count() * 1e-9);
   #endif

   return reversed_BAT;
}




uint64_t address_translation_orig2bolt(uint64_t current_rip,
                             uint64_t orig_func_start_addr, 
                             uint64_t BOLTed_func_start_addr, 
                             map<uint64_t, uint64_t> reversedBAT){
   uint64_t rip_offset = current_rip - orig_func_start_addr;
   // TODO
   uint64_t BB_start_addr = reversedBAT.lower_bound(rip_offset)->first;    
   uint64_t rip_offset_BB = rip_offset - BB_start_addr;
   uint64_t BOLTed_BB_start_addr = reversedBAT[BB_start_addr];
   uint64_t BOLTed_rip_offset = rip_offset_BB + BOLTed_BB_start_addr;
   printf("[tracer] original rip = %lx, BOLTed rip = %lx\n", current_rip, BOLTed_func_start_addr + BOLTed_rip_offset);
   return BOLTed_func_start_addr + BOLTed_rip_offset; 
}




map<uint64_t, uint64_t> gen_bat_from_reversedBat(map<uint64_t, uint64_t>& reversed_bat){
   map<uint64_t, uint64_t> bat; 
   for (auto it = reversed_bat.begin(); it != reversed_bat.end(); it++){
      bat.insert(make_pair(it->second, it->first));
   }
   return bat;
}



uint64_t address_translation_bolt2orig(uint64_t current_rip,
                             uint64_t orig_func_start_addr, 
                             uint64_t BOLTed_func_start_addr, 
                             map<uint64_t, uint64_t> BAT){
   uint64_t rip_offset = current_rip - BOLTed_func_start_addr;
   uint64_t BB_start_addr = BAT.lower_bound(rip_offset)->first;    
   uint64_t rip_offset_BB = rip_offset - BB_start_addr;
   uint64_t orig_BB_start_addr = BAT[BB_start_addr];
   uint64_t orig_rip_offset = rip_offset_BB + orig_BB_start_addr;
   printf("[tracer] original rip = %lx, BOLTed rip = %lx\n", current_rip, orig_func_start_addr + orig_rip_offset);
   return orig_func_start_addr + orig_rip_offset; 
}



