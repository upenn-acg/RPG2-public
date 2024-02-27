#include "utils.hpp"

using namespace std;

/*
 * for each unmoved functions, check any call instruction 
 * within that function and if the call's target is moved,
 * patch the call sites by changing the target.
 */
map<long, vector<vector<uint8_t>>> extract_prefetch_insn(const pg2_env* pg2_environ, unordered_map<long, func_info>);

map<long, vector<vector<uint8_t>>> extract_prefetch_insn_lt(const pg2_env* pg2_environ, unordered_map<long, func_info>);

void change_prefetch_dist_lt(const pg2_env* pg2_environ, int prefetch_dist, map<long, vector<vector<uint8_t>>> prefetch_addr_with_machine_codes);

int convert_last_4bytes2int(vector<uint8_t> machine_codes);

void extract_call_sites(unordered_map<long, func_info> moved_func, const pg2_env* pg2_environ);

// in libelf_extract.a
extern "C" {
  /*
   * Invoke Rust code to extract functions from the given 
   * binary. The starting addresses of functions to be 
   * extracted are passed by an array of long integers.
   */
   void write_functions(const char* bolted_binary_path, const char* vtable_output_file_path, long* function_addrs, long num_addrs);


  /*
   * Invoke Rust code to extract v-tables from the given
   * binary. The arguments are the path of the binary that
   * will have data extracted, and the path to store the 
   * extracted data.
   */ 
   void write_vtable(const char*, const char*);
}
