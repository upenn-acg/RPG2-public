#include "infrastructure.hpp"
#include "perf.hpp"
#include "bolt.hpp"
#include "extract_machine_code.hpp"
#include "ptrace_pause.hpp"
#include <random>

using namespace std;

void inject_BOLTed_function(unordered_map<long, func_info>& bolted_func,
                            map<uint64_t, uint64_t>& reversed_bat,
                            uint64_t &BOLT_starting_addr,
                            uint64_t &original_starting_addr,
                            long &moved_addr,
                            long &original_addr,
                            double &original_IPC,
                            pg2_env &pg2_environ,
                            pid_t targetPID,
                            void* libAddr,
                            float& bolt_time,
                            float& insertion_time);


void initialize_prefetch_dist(pg2_env &pg2_environ,
                              unordered_map<long, func_info>& bolted_func,
                              void* libAddr,
                              pid_t targetPID,
                              map<long, vector<vector<uint8_t>>>& prefetch_addr_with_machine_codes,
                              int initial_prefetch_dist);


void test_different_prefetch_dist(pg2_env &pg2_environ,
                                  void* libAddr,
                                  pid_t targetPID,
                                  int &optimal_pref_dist,
                                  double &optimal_IPC,
                                  map<long, vector<vector<uint8_t>>>& prefetch_addr_with_machine_codes,
                                  int initial_prefetch_dist,
                                  bool should_test_right,
                                  bool should_test_left,
                                  vector<IPC_info> right,
                                  vector<IPC_info> left,
                                  int& num_pd_edit, 
                                  vector<float>& pd_edit_time);

void decide_prefetch_distance_or_revert(pg2_env &pg2_environ,
                                        void* libAddr,
                                        map<uint64_t, uint64_t>& reversed_bat,
                                        pid_t targetPID,
                                        uint64_t original_starting_addr,
                                        uint64_t BOLT_starting_addr,
                                        int &optimal_pref_dist,
                                        double optimal_IPC,
                                        double original_IPC,
                                        map<long, vector<vector<uint8_t>>>& prefetch_addr_with_machine_codes);

int generate_random_number(int min, int max);

void test_prefetch_directions(pg2_env &pg2_environ,
                              void* lib_addr,
                              pid_t target_PID,
                              int &optimal_pref_dist,
                              double &optimal_IPC,
                              map<long, vector<vector<uint8_t>>>& prefetch_addr_with_machine_codes,
                              int initial_prefetch_dist,
                              vector<IPC_info>& right, 
                              vector<IPC_info>& left,
                              bool& should_prefetch_right,
                              bool& should_prefetch_left,
                              vector<float>& pd_edit_time);

void edit_prefetch_dist(pg2_env &pg2_environ,
                        void* lib_addr,
                        pid_t target_PID,
                        int pref_dist,
                        map<long, vector<vector<uint8_t>>>& prefetch_addr_with_machine_codes,
                        float& pd_edit_time);
