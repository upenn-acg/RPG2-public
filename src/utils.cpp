#include "utils.hpp"
using namespace std;


pg2_env::pg2_env(){
   pg2_env::read_config();
   get_dir_path();
   get_cmds();
   
   // this real_target_bin_path is only used in run_llvmbolt()
   pg2_env::bolt_opt_bin_path     = pg2_env::tmp_data_path+target_bin_name+".bolt";
   pg2_env::ld_preload_path       = pg2_env::lib_path+"inject_prefetch.so";

   pg2_env::bolted_function_bin   = pg2_env::tmp_data_path+"bolted_functions.bin";
   pg2_env::v_table_bin           = pg2_env::tmp_data_path+"v_table.bin";
   pg2_env::unmoved_func_bin      = pg2_env::tmp_data_path+"unmoved_func.bin";
   pg2_env::prefetch_insn_bin     = pg2_env::tmp_data_path+"prefetch_insn.bin";
   pg2_env::tmp_prefetch_insn_bin = pg2_env::tmp_data_path+"tmp_prefetch_insn.bin";
   pg2_env::call_sites_list_bin   = pg2_env::tmp_data_path+"call_sites_list.bin";
   pg2_env::call_sites_all_bin    = pg2_env::tmp_data_path+"call_sites_all.bin";
   pg2_env::call_sites_bin        = pg2_env::tmp_data_path+"call_sites.bin";


   pg2_env::perf_path            = pg2_env::get_binary_path("perf");
   pg2_env::nm_path              = pg2_env::get_binary_path("nm");
   pg2_env::objdump_path         = pg2_env::get_binary_path("objdump");

   pg2_env::llvmbolt_path        = pg2_env::get_binary_path("llvm-bolt");
   pg2_env::perf2bolt_path       = pg2_env::get_binary_path("perf2bolt");
   pg2_env::bat_dump_path        = pg2_env::get_binary_path("bat-dump");
   
   pg2_env::listen_fd            = socket(PF_INET, SOCK_STREAM, 0);   
}




void pg2_env::read_config(){
   const char* dir_path = std::getenv("PG2_R_PATH");
   if (!dir_path){
      printf("[tracer][error] please specify environment variable PG2_PATH\n");
      exit(-1);
   }

   string dir_path_str(dir_path); 
   if (dir_path_str[dir_path_str.size()-1] != '/')
      dir_path_str.push_back('/');
   pg2_env::dir_path = dir_path_str;

   string config_s = dir_path_str + "config";
   char* config_cstr = new char[config_s.length()+1];
   strcpy(config_cstr, config_s.c_str()); 

   FILE* config = fopen(config_cstr,"r");
   if (config==NULL){
      printf("%s\n", config_cstr);
      printf("[tracer][error] please place the config file in the same directory with tracer\n ");
      exit(-1);
   }
   free(config_cstr);

   char line[4096];
   while (fgets (line , 4096 , config) != NULL){
      string current_line(line);
      if (current_line[current_line.length()-1]=='\n') current_line.pop_back();

      if ((current_line.length()>0)&&(current_line[0]!='#')){
         string delimiter = "=";
         string bin_name = current_line.substr(0, current_line.find(delimiter));
         string path_name = current_line.substr(current_line.find(delimiter), current_line.length());
         if ((path_name.length()>0)&&(path_name[0]=='=')){
            path_name.erase(path_name.begin());
            pg2_env::configs[bin_name] = path_name;
         }
      }
   } 
}




string pg2_env::get_binary_path(string bin_name){
   if (pg2_env::configs.find(bin_name) != pg2_env::configs.end()){
      return pg2_env::configs[bin_name];
   }
   string cmd = "which "+bin_name;
   char* cmd_cstr = new char[cmd.length()+1];
   strcpy(cmd_cstr,cmd.c_str());
   FILE* fp = popen(cmd_cstr, "r");
   char path[4096];
   if (fp == NULL){
      printf("[tracer][error] Failed to run linux which command\n");
      exit(-1);
   }
   free(cmd_cstr);

   if (fgets(path, sizeof(path), fp)!=NULL){
      string path_str(path);
      if (path_str[path_str.length()-1]=='\n') path_str.pop_back();
      return path_str;
   }
   else{
      printf("[tracer][error] you didn't specify %s in config file, nor did %s exists in your system\n", bin_name.c_str(), bin_name.c_str());
      exit(-1);
   }
   return "";
}



void pg2_env::get_dir_path(){
   pg2_env::tmp_data_path = pg2_env::get_binary_path("tmp_data_dir");
   if (pg2_env::tmp_data_path[pg2_env::tmp_data_path.length()-1] !='/'){
      pg2_env::tmp_data_path.push_back('/');
   }
   pg2_env::lib_path = pg2_env::get_binary_path("lib");
   if (pg2_env::lib_path[pg2_env::lib_path.length()-1] !='/'){
      pg2_env::lib_path.push_back('/');
   }
   // TODO: if the dir path doesn't exist, create a dir path
}




void pg2_env::get_cmds(){
   if (pg2_env::configs.find("cmd")==pg2_env::configs.end()){
      printf("[tracer][error] error in reading `server_cmd` from config file.\n");
      exit(-1);
   }
   pg2_env::cmd = pg2_env::configs["cmd"];
   
   pg2_env::target_bin_path = split_line(pg2_env::cmd)[0];

   vector<string> names = split(pg2_env::target_bin_path, '/');
   if (names.size()==0){
      printf("[tracer][error] error in reading `server_cmd` from config file.\n");
      exit(-1);
   }
   pg2_env::target_bin_name = names[names.size()-1];
}





vector<string> split_line(string str){
   vector<string> words;
   stringstream ss(str);
   string tmp;
   while (ss >> tmp ){
      words.push_back(tmp);
      tmp.clear();
   }
   return words;
}


vector<string> split (const string &s, char delim) {
   vector<string> result;
   stringstream ss (s);
   string item;

   while (getline (ss, item, delim)) {
      result.push_back (item);
   }
   return result;
}


long convert_str_2_int(string str){
   long result = 0;
   for (unsigned i=0; i<str.size(); i++){
      result += str[i] - '0';
      if (i!=str.size()-1){
         result = result * 10;
      }
   }
   return result;
}


bool is_num(string word){
   for (unsigned i=0; i<word.size(); i++){
      if (!((word[i]>='0')&&(word[i]<='9'))){
         return false;
      }
   }
   return true;
}


long convert_str_2_long(string str){
   long result = 0;
   for (unsigned i=0; i<str.size(); i++){
      if ((str[i]>='a')&&(str[i]<='f')){
         result += str[i] -'a'+10;
      }
      else if ((str[i]>='0')&&(str[i]<='9')){
         result += str[i] - '0';
      }
      if (i!=str.size()-1){
         result = result * 16;
      }
   }
   return result;
}


bool is_hex(string word){
   if (word.size()==0) return false;
   for (unsigned int i=0; i<word.size(); i++){
      if (!(((word[i]>='0')&&(word[i]<='9'))||((word[i]>='a')&&(word[i]<='f')))){
         return false;
      }
   }
   return true;
}


bool is_2_bytes_hex(string word){
   if (word.size()!=2) return false;
   for (unsigned int i=0; i<word.size(); i++){
      if (!(((word[i]>='0')&&(word[i]<='9'))||((word[i]>='a')&&(word[i]<='f')))){
         return false;
      }
   }
   return true;
}



uint8_t convert_str_2_uint8(string str){
   uint8_t result = 0;
   if ((str[0]>='a')&&(str[0]<='f')){
      result += str[0] -'a'+10;
   }
   else if ((str[0]>='0')&&(str[0]<='9')){
      result += str[0] - '0';
   }
   result = result * 16;
   if ((str[1]>='a')&&(str[1]<='f')){
      result += str[1] -'a'+10;
   }
   else if ((str[1]>='0')&&(str[1]<='9')){
	   result += str[1] - '0';
   }
   return result;
}



vector<uint8_t> convert_long_2_vec_uint8(long input){
   vector<uint8_t> tmp;
   long divisor = 256*256*256;
   long input_ = input;
   long tmp1;
   for (int i=0 ; i<4; i++){
      tmp1 = input_/divisor;
      input_ = input_%divisor;
      tmp.push_back((uint8_t)tmp1);
      divisor /=256;
   }
   vector<uint8_t> result;
   for (int i=3 ; i>=0; i--){
      result.push_back(tmp[i]);
   }
   return result;
}



string convert_long_2_hex_string(long num){
   stringstream stream;
   stream << std::hex << num;
   string result( stream.str() );
   return result;
}



string convert_long_2_decimal_string(long num){
   stringstream stream;
   stream << num;
   string result (stream.str());
   return result;
}


vector<long> get_keys_to_array(unordered_map<long, func_info> func){
   vector<long> addr_vec;
   for (auto it = func.begin(); it!=func.end(); it++){
      addr_vec.push_back(it->first);
   }
   return addr_vec;
}



vector<long> get_moved_addr_to_array(unordered_map<long, func_info> func){
   vector<long> addr_vec;
   for (auto it = func.begin(); it!=func.end(); it++){
      addr_vec.push_back(it->second.moved_addr);
   }
   return addr_vec;
}


char** split_str_2_char_array(const string &str){
   vector<string> word_vec = split_line(str);
   char** words;
   words = (char**)malloc(sizeof(char*)*word_vec.size()+1);
   for (unsigned i=0; i<word_vec.size(); i++){
      words[i] = (char*)malloc(sizeof(char)*word_vec[i].size()+1); 
      memset(words[i], '\0', sizeof(char)*(word_vec[i].size()+1));
      strcpy(words[i], word_vec[i].c_str());
   }
   words[word_vec.size()] = NULL;
   return words;
}


void clean_up(const pg2_env* pg2_environ){
   string command = "rm -rf "+pg2_environ->tmp_data_path+"bolted_functions.bin "+
                    pg2_environ->tmp_data_path+"*.data "+
                    pg2_environ->tmp_data_path+"*.fdata "+
                    pg2_environ->tmp_data_path+"*.txt "+
                    pg2_environ->tmp_data_path+"*.old ";
   if (system(command.c_str())==-1) exit(-1);
}





bool cmp_pair(pair<string, float>& a, pair<string, float>& b){
   return a.second > b.second;
}
