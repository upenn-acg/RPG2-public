#include "utils.hpp"

using namespace std;

void test_prefetchable_location(const pg2_env* pg2_environ);

unordered_map<long, func_info> run_llvmbolt(const pg2_env*, float& bolt_time);

map<uint64_t, uint64_t> run_bat_dump(const pg2_env*);

uint64_t address_translation_orig2bolt(uint64_t, uint64_t, uint64_t, map<uint64_t, uint64_t>);

uint64_t address_translation_bolt2orig(uint64_t, uint64_t, uint64_t, map<uint64_t, uint64_t>);

map<uint64_t, uint64_t> gen_bat_from_reversedBat(map<uint64_t, uint64_t>& );
