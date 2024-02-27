#include "perf.hpp"

using namespace std;



void run_perf_record(int target_pid, const pg2_env* pg2_environ){
   #ifdef TIME_MEASUREMENT
   auto begin = std::chrono::high_resolution_clock::now();
   #endif

   string command;
   command = pg2_environ->perf_path+
             " record --freq=max -e cpu/event=0xd1,umask=0x20,name=MEM_LOAD_RETIRED.L3_MISS/ppp -o "+
             pg2_environ->tmp_data_path+
             "perf.data -p "+
             to_string(target_pid)+
             " -- sleep 2";
   char * command_cstr = new char [command.length()+1];
   strcpy (command_cstr, command.c_str());
   if (system(command_cstr)!=0) printf("[tracer] error in %s\n",__FUNCTION__);
   free(command_cstr);

   #ifdef TIME_MEASUREMENT
   auto end = std::chrono::high_resolution_clock::now();
   auto elapsed = std::chrono::duration_cast<std::chrono::nanoseconds>(end - begin);
   printf("[tracer(time)] perf record took %f seconds to execute \n", elapsed.count() * 1e-9);
   #endif
}



string run_perf_report(const pg2_env* pg2_environ){
   #ifdef TIME_MEASUREMENT
   auto begin = std::chrono::high_resolution_clock::now();
   #endif

   FILE *fp1;
   char path1[3000];

   string command;
   command = pg2_environ->perf_path+
             " report --stdio -i "+
             pg2_environ->tmp_data_path+
             "perf.data";
   char* command_cstr = new char[command.length()+1];
   strcpy(command_cstr, command.c_str()); 
   fp1 = popen(command_cstr, "r");
   free(command_cstr);

   if (fp1 == NULL){
      printf("Failed to run llvm-bolt command\n" );
      exit(-1);
   }

   while (fgets(path1, sizeof(path1), fp1) != NULL) {
      string line(path1);
      vector<string> words = split_line(line);
      if ((words.size()>0)&&(words[0]=="#")) continue;
      if ((words.size()>4)&&(words[3]=="[.]")) {
         // handle error cases in perf report
         if (words[2]!=pg2_environ->target_bin_name) continue;
         // if the function is from dynamic linking library
         // also skip the function
         if (words[4].size()>4) {
            string last4letters = words[4].substr(words[4].size()-4, words[4].size()-1);
            if (last4letters == "@plt") continue;
         }

         #ifdef TIME_MEASUREMENT
         auto end = std::chrono::high_resolution_clock::now();
         auto elapsed = std::chrono::duration_cast<std::chrono::nanoseconds>(end - begin);
         printf("[tracer(time)] perf report took %f seconds to execute \n", elapsed.count() * 1e-9);
         #endif

         printf("[tracer] top LLC miss function is %s\n", words[4].c_str());
         return words[4];
      }
   }
   printf("[tracer][error] error in %s\n", __FUNCTION__); 
   exit(-1);
   return "";
}



void run_perf_script(string func_name, const pg2_env* pg2_environ){
   #ifdef TIME_MEASUREMENT
   auto begin = std::chrono::high_resolution_clock::now();
   #endif

   FILE *fp1;
   char path1[3000];

   string command;
   command = pg2_environ->perf_path+
             " annotate --stdio -M att -i "+
             pg2_environ->tmp_data_path+
             "perf.data "+func_name;
   char* command_cstr = new char[command.length()+1];
   strcpy(command_cstr, command.c_str()); 
   fp1 = popen(command_cstr, "r");
   free(command_cstr);

   if (fp1 == NULL){
      printf("Failed to run llvm-bolt command\n" );
      exit(-1);
   }

   float highest_percentage = 0;
   vector<pair<string, float>> addr_and_percentage;
   while (fgets(path1, sizeof(path1), fp1) != NULL) {
      string line(path1);
      vector<string> words = split_line(line);
      if (words.size()==0) continue;
      if (words.size()==1) continue;
      else if (words[0]==":") continue;
      else if (words[1]!=":") continue;
      float percentage = std::stof(words[0]);
      if (percentage > 10.0){
         string addr = words[2];
         addr.pop_back();
         addr_and_percentage.push_back(make_pair(addr, percentage));
      }
      if (percentage > highest_percentage){ 
         highest_percentage = percentage;
      }
   } 

   // Sort using comparator function
   sort(addr_and_percentage.begin(), addr_and_percentage.end(), cmp_pair);
 
   FILE *fp2;
   string path = pg2_environ->tmp_data_path+"prefetch_loc.txt";
   fp2 = fopen(path.c_str(), "w");
   fprintf(fp2, "%s ", func_name.c_str());
   
   for (unsigned i=0; i<addr_and_percentage.size(); i++){
      fprintf(fp2, "%s 512 ", addr_and_percentage[i].first.c_str()); 
   }

   fclose(fp2);

   #ifdef TIME_MEASUREMENT
   auto end = std::chrono::high_resolution_clock::now();
   auto elapsed = std::chrono::duration_cast<std::chrono::nanoseconds>(end - begin);
   printf("[tracer(time)] perf annotate took %f seconds to execute \n", elapsed.count() * 1e-9);
   #endif
}





double run_perf_stat(const pg2_env*, pid_t target_pid){
   string PID = convert_long_2_decimal_string(target_pid);
   string command = "perf stat -e cycles:u,instructions:u -p "+PID+" -- sleep 0.3 2>&1";

   #ifdef DEBUG_INFO
   cout<<"---------------run_perf_stat-----------------\n";
   cout<<"[tracer] cmd: "<<command<<endl;
   #endif

   char* command_cstr = new char [command.length()+1];
   strcpy (command_cstr, command.c_str());

   FILE* fp = popen(command_cstr, "r");

   if (fp == NULL){
      printf("Fail to run command ps\n" );
      exit(-1);
   }

   char path[1000];
   double num_cycles = 0;
   double num_insn = 0;
   while (fgets(path, sizeof(path), fp) != NULL) {
      string line(path);
      #ifdef DEBUG_INFO
      cout<<line;
      #endif
      vector<string> words = split_line(line);
      if (words.size()>1){
         if (words[1]=="cycles:u"){
            string num_cycles_str = words[0];
            num_cycles = (double)(convert_str_2_int(num_cycles_str));
         }
         else if (words[1]=="instructions:u"){
            string num_insn_str = words[0];
            num_insn = (double)(convert_str_2_int(num_insn_str));
         }
         
      }
   }
   if (num_cycles==0) {
      printf("[tracer] perf stat: number of cycles is 0\n");
      exit(-1);
   }
   double IPC = num_insn/num_cycles;
   
   #ifdef DEBUG_INFO
   printf("[tracer] IPC = %lf\n", IPC);
   #endif

   fclose(fp);
   free(command_cstr);

   return IPC;
}



