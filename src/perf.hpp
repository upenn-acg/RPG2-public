#include "utils.hpp"

using namespace std;

void run_perf_record(int target_pid, const pg2_env*);

string run_perf_report(const pg2_env*);

void run_perf_script(string, const pg2_env*);

double run_perf_stat(const pg2_env*, pid_t);

