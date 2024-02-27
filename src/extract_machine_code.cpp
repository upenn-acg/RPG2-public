#include "extract_machine_code.hpp"
#include "boost_serialization.hpp"

using namespace std;

map<long, vector<vector<uint8_t> > > extract_prefetch_insn(const pg2_env* pg2_environ, unordered_map<long, func_info> bolted_func){
   map<long, vector<vector<uint8_t> > > prefetch_addr_with_machine_codes;

   for (auto it = bolted_func.begin(); it != bolted_func.end(); it++){
      FILE *fp;
      char path[1000];
      string start_addr = convert_long_2_hex_string(it->second.moved_addr);
      string stop_addr = convert_long_2_hex_string(it->second.moved_addr+it->second.moved_size);
      string command = pg2_environ->objdump_path + " -d --insn-width=10 "+ 
                       " --start-address=0x"+ start_addr + 
                       " --stop-address=0x"+ stop_addr + 
                       " " + pg2_environ->bolt_opt_bin_path;
      char * command_cstr = new char [command.length()+1];
      strcpy (command_cstr, command.c_str());

      fp = popen(command_cstr, "r");
      while (fp == NULL) {
         printf("Failed to run command\n" );
         sleep(1);
         fp = popen(command_cstr, "r");
      }

      vector<string> assembly_lines;
      while (fgets(path, sizeof(path), fp) != NULL) {
         string line(path);
         assembly_lines.push_back(line);
      }
      delete command_cstr;
      fclose(fp);

      int prefetch_line_num = 0;
      uint64_t starting_addr = 0;
      vector<vector<uint8_t>> machine_codes;

      bool has_prefetch = false;
      for (unsigned int i=0; i<assembly_lines.size(); i++){
         vector<string> words = split_line(assembly_lines[i]);
         if (words.size()>3){
            // machine code for prefetch is "0f 18"
            if ((words[1]=="0f")&&(words[2]=="18")){
               prefetch_line_num = i;
               has_prefetch = true;
               break;
            }
            else if (words[words.size()-2]=="prefetcht0"){
               prefetch_line_num = i;
               has_prefetch = true;
               break;
            }
         }
      }

      if (!has_prefetch){
         printf("[tracer] the BOLTed binary doesn't contain prefetch instructions\n");
         printf("[tracer] please check the prefetch_loc.txt file. The top LLC miss instr might not be prefetchable\n");
         exit(1);
      }

      for (unsigned k = 0; k < it->second.prefetch_locations.size(); k++){
         for (int i = prefetch_line_num - it->second.prefetch_locations[k].second; i<=prefetch_line_num - it->second.prefetch_locations[k].first; i++){
            vector<string> words = split_line(assembly_lines[i]);
            if (i== (prefetch_line_num - it->second.prefetch_locations[k].second)){
               string starting_addr_str = words[0].substr(0, words[0].size()-1);
               starting_addr = convert_str_2_long(starting_addr_str);
            }
            vector<uint8_t> machine_code;
            machine_code.clear();
            for (unsigned int j=0; j<words.size(); j++){
               if (is_2_bytes_hex(words[j])){
                  machine_code.push_back(convert_str_2_uint8(words[j]));
               }
            }
            machine_codes.push_back(machine_code);
         }
         prefetch_addr_with_machine_codes.insert(make_pair(starting_addr, machine_codes));
      }
   }

   return prefetch_addr_with_machine_codes;  
}




map<long, vector<vector<uint8_t> > > extract_prefetch_insn_lt(const pg2_env* pg2_environ, unordered_map<long, func_info> bolted_func){
   map<long, vector<vector<uint8_t> > > prefetch_addr_with_machine_codes;

   for (auto it = bolted_func.begin(); it != bolted_func.end(); it++){
      FILE *fp;
      char path[1000];
      string start_addr = convert_long_2_hex_string(it->second.moved_addr);
      string stop_addr = convert_long_2_hex_string(it->second.moved_addr+it->second.moved_size);
      string command = pg2_environ->objdump_path + " -d --insn-width=10 "+ 
                       " --start-address=0x"+ start_addr + 
                       " --stop-address=0x"+ stop_addr + 
                       " " + pg2_environ->bolt_opt_bin_path;
      char * command_cstr = new char [command.length()+1];
      strcpy (command_cstr, command.c_str());

      fp = popen(command_cstr, "r");
      while (fp == NULL) {
         printf("Failed to run command\n" );
         sleep(1);
         fp = popen(command_cstr, "r");
      }

      vector<string> assembly_lines;
      while (fgets(path, sizeof(path), fp) != NULL) {
         string line(path);
         assembly_lines.push_back(line);
      }
      delete command_cstr;
      fclose(fp);

      int prefetch_line_num = 0;
      int add_line_num = 0;
      uint64_t starting_addr = 0;
      vector<vector<uint8_t>> machine_codes;

      bool has_prefetch = false;
      for (unsigned int i=0; i<assembly_lines.size(); i++){
         vector<string> words = split_line(assembly_lines[i]);
         if (words.size()>3){
            // machine code for prefetch is "0f 18"
            if ((words[1]=="0f")&&(words[2]=="18")){
               prefetch_line_num = i;
               has_prefetch = true;
               break;
            }
         }
      }

      if (!has_prefetch){
         printf("[tracer] the BOLTed binary doesn't contain prefetch instructions\n");
         printf("[tracer] please check the prefetch_loc.txt file. The top LLC miss instr might not be prefetchable\n");
         exit(1);
      }

      for (int i=prefetch_line_num; i>=0; i--){
         vector<string> words = split_line(assembly_lines[i]);
         if (words.size()>3){
            // machine code for prefetch is "0f 18"
            if (words[words.size()-2]=="add"){
               add_line_num = i;
               string starting_addr_str = words[0].substr(0, words[0].size()-1);
               starting_addr = convert_str_2_long(starting_addr_str);
               break;
            }
         }
      }

      for (int i=add_line_num; i<prefetch_line_num; i++){ 
         vector<string> words = split_line(assembly_lines[i]);
         vector<uint8_t> machine_code;
         machine_code.clear();
         for (unsigned int j=0; j<words.size(); j++){
            if (is_2_bytes_hex(words[j])){
               machine_code.push_back(convert_str_2_uint8(words[j]));
            }
         }
         machine_codes.push_back(machine_code);
      }
      prefetch_addr_with_machine_codes.insert(make_pair(starting_addr, machine_codes));
   }
   return prefetch_addr_with_machine_codes;  
}


int convert_last_4bytes2int(vector<uint8_t> machine_codes){
   int result = 0;
   int tmp = 1;
   if (machine_codes.size()<5) {
      printf("[tracer] error in %s\n", __FUNCTION__);
      exit(1);
   }
   for (unsigned i = 0; i < 4; i++) {
      result += (int)(machine_codes[machine_codes.size()-4+i]) * tmp; 
      tmp *= 16;
   }
   return result;
}




void change_prefetch_dist_lt(const pg2_env* pg2_environ, int prefetch_dist, map<long, vector<vector<uint8_t>>> prefetch_addr_with_machine_codes ){
   #ifdef DEBUG_INFO
   printf("----------------------------\n");
   printf("[tracer] new prefetch dist = %d\n", prefetch_dist);
   #endif
   FILE *pFile2 = fopen(pg2_environ->tmp_prefetch_insn_bin.c_str(),"w");

   if (pFile2!=NULL){
      for(auto it=prefetch_addr_with_machine_codes.begin(); it!=prefetch_addr_with_machine_codes.end(); it++){
         long address = it->first;
         int num = 0;

         #ifdef DEBUG_INFO
         printf("[tracer] function address: %lx\n",address);
         #endif

         for (unsigned int i=0; i<it->second.size(); i++){
            num +=(int)it->second[i].size();
         }

         // write back to tmp file
         fwrite(&address, sizeof(long), 1, pFile2);
         fwrite(&num, sizeof(int), 1, pFile2);
   
         vector<uint8_t> add_instr = it->second[0];
         vector<uint8_t> instr_before_prefetch = it->second[it->second.size()-1];

         int offset_add_instr = convert_last_4bytes2int(add_instr);  
         int offset_instr_before_prefetch = convert_last_4bytes2int(instr_before_prefetch);  
         int scale= offset_instr_before_prefetch / offset_add_instr;

         for (unsigned int i=0; i<it->second.size(); i++){
            int len = (int)it->second[i].size(); 
            uint8_t machine_code[len];
            std::copy(it->second[i].begin(), it->second[i].end(), machine_code);
            if (i==0){
               if (prefetch_dist<256){
                  machine_code[len-4] = (uint8_t)(prefetch_dist);
                  machine_code[len-3] = 0;
               }
               else if (prefetch_dist<4096){
                  machine_code[len-4] = (uint8_t)(prefetch_dist%256);
                  machine_code[len-3] = (uint8_t)(prefetch_dist/256);
               }
            }
            else if (i==(it->second.size()-1)){
               if (prefetch_dist * scale<256){    
                  machine_code[len-4] = (uint8_t)(prefetch_dist * scale);
                  machine_code[len-3] = 0;
               }
               else if (prefetch_dist * scale<4096){
                  machine_code[len-4] = (uint8_t)((prefetch_dist * scale)%256);
                  machine_code[len-3] = (uint8_t)((prefetch_dist * scale)/256);             
               }
               else{
                  // TODO
                  printf("[tracer][error] pg2 doesn't support prefetch distance greater than 512\n");
                  exit(-1);
               }
            }
            #ifdef DEBUG_INFO
            printf("[tracer] ");
            for (int i=0; i<len; i++){
               printf("%x ", (int)machine_code[i]);
            }
            printf("\n");
            #endif

            fwrite(machine_code, sizeof(uint8_t), len, pFile2);
         }
      }
   }
   else{
      printf("[tracee] cannot open prefetch_insn.bin\n");
      exit(-1);
   }
   fclose(pFile2);
}




void extract_call_sites(unordered_map<long, func_info> moved_func, const pg2_env* pg2_environ){
   FILE *pFile = fopen(pg2_environ->call_sites_bin.c_str(),"w");
   // <starting address, call_sites_info>
   unordered_map<long, call_site_info> call_sites;
   const string file = pg2_environ->call_sites_all_bin;
   ifstream filestream(file);
   boost::archive::binary_iarchive archive(filestream);
   archive >> call_sites;

   // <target address, caller inst addresses>
   unordered_map<long, vector<long> > call_sites_list;
   ifstream filestream1(pg2_environ->call_sites_list_bin);
   boost::archive::binary_iarchive archive1(filestream1);
   archive1 >> call_sites_list;

   for (auto it = moved_func.begin(); it!=moved_func.end(); it++){
      if (call_sites_list.find(it->first)!=call_sites_list.end()){
         vector<long> caller_lists = call_sites_list[it->first];
         for (unsigned i=0; i<caller_lists.size(); i++){
            long addr = caller_lists[i];
            long base_addr = call_sites[addr].next_addr;
            long new_target_addr = it->second.moved_addr;
            long offset = new_target_addr - base_addr;
            vector<uint8_t> machine_code_line = convert_long_2_vec_uint8(offset);
            // write the virtual address + the size of the machine code
            // and machine code itself into a file
            long machine_code_address = addr;
            long machine_code_size = (long)(machine_code_line.size()+1);
            fwrite(&machine_code_address, sizeof(long), 1, pFile);
            fwrite(&machine_code_size, sizeof(long), 1, pFile);
            uint8_t buffer[machine_code_line.size()+1];

            buffer[0]= (uint8_t)232;
            for (unsigned i=0; i<machine_code_line.size(); i++){
               buffer[i+1] = machine_code_line[i];
            }
            fwrite (buffer , sizeof(uint8_t), machine_code_line.size()+1, pFile);
         }
      }
   }
   fflush(pFile);
   fclose(pFile);
}
