#include "infrastructure.hpp"

using namespace std;



void createTargetProcess(const pg2_env* pg2_environ){
   string ld_pre = "LD_PRELOAD="+ pg2_environ->ld_preload_path;
   char* ldpreload = new char[ld_pre.length()+1];
   memset(ldpreload, 0, ld_pre.length()+1);
   strcpy(ldpreload, ld_pre.c_str());

   string exe_cmd = pg2_environ->cmd;
   char** argv = split_str_2_char_array(exe_cmd);
   putenv(ldpreload);
   char **envp = environ;

   int ret = execve(argv[0], argv, envp);
   if (ret==-1){
      printf("[tracer] fail to create the program\n");
      perror("[tracer] execve: "); 
      exit(-1);
   }
}



void createTCPsocket(int listen_fd, struct sockaddr_in & servaddr){
   bzero(&servaddr, sizeof(servaddr));
   servaddr.sin_family = AF_INET;
   servaddr.sin_addr.s_addr = htons(INADDR_ANY);
   servaddr.sin_port = htons(PORT1);
   bind(listen_fd, (struct sockaddr*)&servaddr, sizeof(servaddr));
   listen(listen_fd, 10);
}





void* get_lib_addr(int listen_fd){
   struct sockaddr_in clientaddr;
   socklen_t clientaddrlen = sizeof(clientaddr);
   int comm_fd = accept(listen_fd, (struct sockaddr*)&clientaddr, &clientaddrlen);
   const int enable = 1;
   if (setsockopt(comm_fd, SOL_SOCKET, SO_REUSEADDR, &enable, sizeof(int)) < 0){
      printf("setsockopt(SO_REUSEADDR) failed");
      exit(-1);
   }

   printf("[tracer] connection from %s\n", inet_ntoa(clientaddr.sin_addr));
   char* buf = (char*)malloc(100*sizeof(char));
   int n = read(comm_fd, buf, 50);
   if (n<=0){
      printf("[tracer] error in receiving msg from tracee.\n");
   }
   string addr(buf);
   free(buf);
   void* lib_addr = (void*)(convert_str_2_int(addr));		
   printf("[tracer] the received address is: %p\n", lib_addr);
   close(listen_fd);
   return lib_addr;
}




void send_data_path(const pg2_env* pg2_environ){
   const int enable = 1;

   int listen_fd = socket(PF_INET, SOCK_STREAM, 0);
   if (setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, &enable, sizeof(int)) < 0){
      printf("setsockopt(SO_REUSEADDR) failed");
      exit(-1);
   }

   struct sockaddr_in servaddr;
   bzero(&servaddr, sizeof(servaddr));
   servaddr.sin_family = AF_INET;
   servaddr.sin_addr.s_addr = htons(INADDR_ANY);
   servaddr.sin_port = htons(PORT2);
   bind(listen_fd, (struct sockaddr*)&servaddr, sizeof(servaddr));
   listen(listen_fd, 10);

   socklen_t servaddrlen = sizeof(servaddr);
   int comm_fd = accept(listen_fd, (struct sockaddr*)&servaddr, &servaddrlen);
   if (setsockopt(comm_fd, SOL_SOCKET, SO_REUSEADDR, &enable, sizeof(int)) < 0){
      printf("setsockopt(SO_REUSEADDR) failed");
      exit(-1);
   }
   printf("[tracer] connection from %s\n", inet_ntoa(servaddr.sin_addr));


   int sockfd = socket(PF_INET, SOCK_STREAM, 0);
   if (sockfd < 0) {
      printf("[tracer] cannot open socket (%s)\n", strerror(errno));
      exit(-1);
   }
   if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &enable, sizeof(int)) < 0){
      printf("setsockopt(SO_REUSEADDR) failed");
      exit(-1);
   }
   // open a socket, connect to the tracer's parent process
   // and sends the address of insert_machine_code() to 
   // tracer
   struct sockaddr_in servaddr2;
   bzero(&servaddr2, sizeof(servaddr2));
   servaddr2.sin_family = AF_INET;
   servaddr2.sin_port = htons(PORT3);
   inet_pton(AF_INET, "localhost", &(servaddr2.sin_addr));
   connect(sockfd, (struct sockaddr*)&servaddr2, sizeof(servaddr2));

   // convert the virtual address of insert_machine_code()
   string path = pg2_environ->tmp_data_path;
   char* buf = (char*) malloc(sizeof(char)*path.size());
   strcpy(buf, path.c_str());
   int n = write(sockfd, buf, path.size());
   if (n <= 0) exit(-1);
   free(buf);
   close(sockfd);
   close(comm_fd);
   close(listen_fd);
}





void write_TopLLCMiss_info_to_file(string func_name, string addr, const pg2_env* pg2_environ){
   FILE *fp1;
   string path =pg2_environ->tmp_data_path+"prefetch_loc.txt";
   fp1 = fopen(path.c_str(), "w");
   fprintf(fp1, "%s %s 512", func_name.c_str(), addr.c_str());
   fclose(fp1);  
}




void compute_new_prefetch_dist(vector<IPC_info>& IPC_PrefDist){
   if (IPC_PrefDist.size() == 1){
      IPC_info new_info(0,IPC_PrefDist[0].prefetch_distance+5);
      IPC_PrefDist.push_back(new_info);
      return;
   }
   if (IPC_PrefDist.size() == 2){
      int x = IPC_PrefDist[0].prefetch_distance;
      int y = IPC_PrefDist[1].prefetch_distance;
      IPC_info new_info(0, y+2*(y-x));
      IPC_PrefDist.push_back(new_info);
      return; 
   }

   int x = IPC_PrefDist[0].prefetch_distance;
   int y = IPC_PrefDist[1].prefetch_distance;
   int z = IPC_PrefDist[2].prefetch_distance;

   double a = IPC_PrefDist[0].IPC;
   double b = IPC_PrefDist[1].IPC;
   double c = IPC_PrefDist[2].IPC;

   if (z == (y + 2*(y-x))) {
      if (c>=b){
         IPC_PrefDist.erase(IPC_PrefDist.begin());
         IPC_info new_info(0, z+2*(z-y));
         IPC_PrefDist.push_back(new_info);
         return;
      }
      else{
         IPC_PrefDist.erase(IPC_PrefDist.begin());
         IPC_info new_info(0, (y+z)/2);
         IPC_PrefDist.push_back(new_info);
         return;
      }
   } 
   
   if (z == ((x+y)/2)){
      if (a > b){
         if (a >= c){
            // erase b (y)
            IPC_PrefDist.erase(IPC_PrefDist.begin()+1);
            IPC_info new_info(0, (x+z)/2);
            IPC_PrefDist.push_back(new_info);
            return;
         }
         else {
            IPC_PrefDist.front().IPC = c;
            IPC_PrefDist.front().prefetch_distance = z;
            IPC_PrefDist.pop_back();
            IPC_info new_info(0, (y+z)/2);
            IPC_PrefDist.push_back(new_info);
            return;
         }
      }
      else {
         if (b >= c){
            IPC_PrefDist.front().IPC = c;
            IPC_PrefDist.front().prefetch_distance = z;
            IPC_PrefDist.back().IPC =0;
            IPC_PrefDist.back().prefetch_distance = (y + z)/2;
            return;
         }
         else {
            IPC_PrefDist.erase(IPC_PrefDist.begin()+1);
            IPC_info new_info(0, (x+z)/2);
            IPC_PrefDist.push_back(new_info);
            return;
         }
      }
   }
   printf("[tracer][error] error in compute_new_prefetch_dist()\n");
   exit(-1);
}

bool should_stop(vector<IPC_info> IPC_prefDist){
   int size = (int)IPC_prefDist.size();
   if (size == 1) return false;
   if (size == 2) return false;

   int x = IPC_prefDist[0].prefetch_distance;
   int y = IPC_prefDist[1].prefetch_distance;
   int z = IPC_prefDist[2].prefetch_distance;

   if (z == (y + 2*(y-x))){
      if (z>300) return true;
      else return false;
   }

   if (z == (x+y)/2){
      if (((x-z) == 1) || ((y-z)==1)) return true;
      else return false;
   }

   printf("[tracer][error] error in should_stop()\n");
   printf("x=%d, y=%d, z=%d\n", x, y, z);
   exit(-1);
}




void compute_new_prefetch_dist_left(vector<IPC_info>& IPC_PrefDist){
   if (IPC_PrefDist.size() == 1){
      IPC_info new_info(0,IPC_PrefDist[0].prefetch_distance-5);
      IPC_PrefDist.push_back(new_info);
      return;
   }
   if (IPC_PrefDist.size() == 2){
      int x = IPC_PrefDist[0].prefetch_distance;
      int y = IPC_PrefDist[1].prefetch_distance;
      if ((y-2*(x-y))>0){
         IPC_info new_info(0, y-2*(x-y));
         IPC_PrefDist.push_back(new_info);
      }
      else {
         IPC_info new_info(0, 3);
         IPC_PrefDist.push_back(new_info);
      }
      return; 
   }

   int x = IPC_PrefDist[0].prefetch_distance;
   int y = IPC_PrefDist[1].prefetch_distance;
   int z = IPC_PrefDist[2].prefetch_distance;

   double a = IPC_PrefDist[0].IPC;
   double b = IPC_PrefDist[1].IPC;
   double c = IPC_PrefDist[2].IPC;

   if (z == (y - 2*(x-y))) {
      if (c>=b){
         IPC_PrefDist.erase(IPC_PrefDist.begin());
         if ((z-2*(y-z)>0)){
            IPC_info new_info(0, z-2*(y-z));
            IPC_PrefDist.push_back(new_info);
         }
         else{
            IPC_info new_info(0, 3);
            IPC_PrefDist.push_back(new_info); 
         }
         return;
      }
      else{
         IPC_PrefDist.erase(IPC_PrefDist.begin());
         IPC_info new_info(0, (y+z)/2);
         IPC_PrefDist.push_back(new_info);
         return;
      }
   } 
   
   if (z == ((x+y)/2)){
      if (a > b){
         if (a >= c){
            // erase b (y)
            IPC_PrefDist.erase(IPC_PrefDist.begin()+1);
            IPC_info new_info(0, (x+z)/2);
            IPC_PrefDist.push_back(new_info);
            return;
         }
         else {
            IPC_PrefDist.front().IPC = c;
            IPC_PrefDist.front().prefetch_distance = z;
            IPC_PrefDist.pop_back();
            IPC_info new_info(0, (y+z)/2);
            IPC_PrefDist.push_back(new_info);
            return;
         }
      }
      else {
         if (b >= c){
            IPC_PrefDist.front().IPC = c;
            IPC_PrefDist.front().prefetch_distance = z;
            IPC_PrefDist.back().IPC =0;
            IPC_PrefDist.back().prefetch_distance = (y + z)/2;
            return;
         }
         else {
            IPC_PrefDist.erase(IPC_PrefDist.begin()+1);
            IPC_info new_info(0, (x+z)/2);
            IPC_PrefDist.push_back(new_info);
            return;
         }
      }
   }
   printf("[tracer][error] error in compute_new_prefetch_dist()\n");
   exit(-1);
}



bool should_stop_left( vector<IPC_info> IPC_prefDist){
   int size = (int)IPC_prefDist.size();
   if (IPC_prefDist[size-1].prefetch_distance < 5) return true;
   if (size == 1) return false;
   if (size == 2) return false;

   int x = IPC_prefDist[0].prefetch_distance;
   int y = IPC_prefDist[1].prefetch_distance;
   int z = IPC_prefDist[2].prefetch_distance;

   if (z == (y - 2*(x-y))){
      if (z<5) return true;
      else return false;
   }

   if (z == (x+y)/2){
      if (((x-z) == 5) || ((y-z)==5)) return true;
      else return false;
   }

   printf("[tracer][error] error in should_stop()\n");
   printf("x=%d, y=%d, z=%d\n", x, y, z);
   exit(-1);
}






unordered_map<long, func_info> get_func_with_original_addr(const pg2_env* pg2_environ){
   FILE *fp;
   char path[3000];
   string command = "" + pg2_environ->nm_path + " -S -n "+ pg2_environ->target_bin_path;
   char* command_cstr = new char[command.length()+1];
   strcpy (command_cstr, command.c_str());
   fp = popen(command_cstr, "r");
   free(command_cstr);
   if (fp == NULL){
      printf("Failed to run nm on original binary\n" );
      exit(-1);
   }

   vector<string> lines;
   while (fgets(path, sizeof(path), fp) != NULL) {
      string line(path);
      lines.push_back(line);
   }

   unordered_map<long, func_info>	func_with_addr;
   for (unsigned i=0; i<lines.size(); i++){
      string line = lines[i];
      vector<string> words = split_line(line);
      if (words.size()>3){
         if ((words[2]=="T")||(words[2]=="t")){
            long addr = convert_str_2_long(words[0]);
            if (func_with_addr.find(addr)==func_with_addr.end()){
               func_info new_func;
               new_func.func_name     = words[3];
               new_func.original_addr = addr;
               new_func.original_size = convert_str_2_long(words[1]);
               new_func.orig_addr_str = words[0];
               func_with_addr[addr] = new_func;
            }
         }
      }
   }
   #ifdef MEASUREMENT
   printf("[tracer] %ld functions are in the target process \n", func_with_addr.size());
   #endif
   fclose(fp);
   return func_with_addr;
}



unordered_map<long, func_info> get_unmoved_func(const pg2_env* pg2_environ, 
                                                unordered_map<long, func_info> bolted_func)
{
   FILE *fp;
   char path[3000];
   string command = "" + pg2_environ->nm_path + " -S -n "+ pg2_environ->bolt_opt_bin_path;
   char* command_cstr = new char[command.length()+1];
   strcpy (command_cstr, command.c_str());
   fp = popen(command_cstr, "r");
   free(command_cstr);
   if (fp == NULL){
      printf("Failed to run nm on original binary\n" );
      exit(-1);
   }

   vector<string> lines;
   while (fgets(path, sizeof(path), fp) != NULL) {
      string line(path);
      lines.push_back(line);
   }

   unordered_map<long, func_info>	func_with_addr;
   for (unsigned i=0; i<lines.size(); i++){
      string line = lines[i];
      vector<string> words = split_line(line);
      if (words.size()>3){
         if ((words[2]=="T")||(words[2]=="t")){
            long addr = convert_str_2_long(words[0]);
            if (func_with_addr.find(addr)==func_with_addr.end()){
               func_info new_func;
               new_func.func_name     = words[3];
               new_func.original_addr = addr;
               new_func.original_size = convert_str_2_long(words[1]);
               new_func.orig_addr_str = words[0];
               func_with_addr[addr] = new_func;
            }
         }
      }
   }

   unordered_map<long, func_info> unmoved_func;
   for(auto it = func_with_addr.begin(); it != func_with_addr.end(); it++){
      if (bolted_func.find(it->first)==bolted_func.end()){
         unmoved_func[it->first] = it->second;
      }
   }
   #ifdef MEASUREMENT
   printf("[tracer(measure)] the size of unmoved_func is: %lu\n",unmoved_func.size());
   printf("[tracer(measure)] the size of orig_func is: %lu\n",func_with_addr.size());
   #endif
   return unmoved_func;
}



map<long, func_info> change_func_to_heap(unordered_map<long, func_info> func){
   map<long, func_info> func_heap;
   for(auto it = func.begin(); it != func.end(); it++){
      func_heap[it->first] = it->second;
   }
   return func_heap;
}





unordered_map<long, func_info> get_func_in_call_stack(vector<unw_word_t> call_stack_ips, 
                                                      map<long, func_info> unmoved_func_heap)
{
   unordered_map<long, func_info> func_in_call_stack;

   for (unsigned i = 0; i < call_stack_ips.size(); i++){
      auto it_low = unmoved_func_heap.lower_bound(call_stack_ips[i]);
      if (it_low!=unmoved_func_heap.end()){
         auto it = prev(it_low);
         if (it!=unmoved_func_heap.end()){
           func_in_call_stack[it->first] = it-> second;
         }
      }
   }
   #ifdef MEASUREMENT
   printf("[tracer] number of function in call stack: %u\n",func_in_call_stack.size());
   #endif
   return func_in_call_stack;
}


void write_func_on_call_stack_into_file(const pg2_env* pg2_environment, 
                                        unordered_map<long, func_info> func_in_call_stack){
  string snapshot_path = pg2_environment->tmp_data_path + "callstack_func.bin";
  FILE* fp = fopen(snapshot_path.c_str(), "w");

  long callstack_func_number = func_in_call_stack.size();
  fwrite(&callstack_func_number, sizeof(long), 1, fp);

  uint64_t buffer[func_in_call_stack.size()];
  int i = 0; 
  for (auto it = func_in_call_stack.begin(); it != func_in_call_stack.end(); it++){
     buffer[i] = (uint64_t)it->first;
     i++;
  }
  fwrite(buffer, sizeof(uint64_t), callstack_func_number, fp);

  fflush(fp);
  fclose(fp);
}





void wait_for_starting_signal(){
  sigset_t set;
  sigemptyset(&set);
  if(sigaddset(&set, SIGUSR1) == -1){
    printf("Sigaddset error");
  }
  int sig;
  if(sigwait(&set, &sig) != 0) {
    printf("Sigwait error");
  }
}
