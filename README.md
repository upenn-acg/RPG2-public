# RPG^2: Robust Profile-Guided Runtime Prefetch Generation
RPG^2 is a pure-software system that operates on running C/C++ programs, profiling them, injecting prefetch instructions, and then tuning those prefetches to maximize performance. Across dozens of inputs, we find that RPG^2 can provide speedups of up to Max Speedup, comparable to the best profile-guided prefetching compilers, but can also respond when prefetching ends up being harmful and roll back to the original code -- something that static compilers cannot. RPG^2 improves prefetching robustness by preserving its performance benefits, while avoiding slowdowns. 
- A description of how we implemented RPG^2 and experimental results of RPG^2 are in [ASPLOS'24 paper](https://dl.acm.org/doi/10.1145/3620665.3640396)

## Note
We only tested the BOLT pass [InjectPrefetchPass.cpp](https://github.com/upenn-acg/BOLT/blob/rpg2/bolt/lib/Passes/InjectPrefetchPass.cpp) for the C/C++ programs that are compiled by clang-10 on the Intel Xeon Gold 6230R Cascade Lake and Intel Xeon(R) CPU E5-2618L v3 Haswell servers with Linux version 5.40. For other settings, we cannot guarantee the BOLT pass we developed works well. 

## Prerequisites
Please refer instructions from links or directly run commands listed below to install prerequisites: 
- Linux Perf:`sudo apt-get install linux-tools-common linux-tools-generic` 
- libunwind: [https://github.com/libunwind/libunwind](https://github.com/libunwind/libunwind) 
- Rust: `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh` 
- binutils (for objdump) [^1] : [https://ftp.gnu.org/gnu/binutils/](https://ftp.gnu.org/gnu/binutils/) 
- boost: `sudo apt-get install libboost-all-dev` 
[^1]:If your `objdump` version is older than 2.27, please download the latest version of `binutils`.  


## Build BOLT from source
To use `llvm-bolt` utilities, `BOLT` needs to be installed. \
Please follow the commands below to install `BOLT` 
```bash
> mkdir BOLT && cd BOLT
> git clone git@github.com:upenn-acg/BOLT.git llvm-bolt
> cd llvm-bolt 
> git checkout rpg2
> cd ..
> mkdir build && cd build
> cmake -G "Unix Makefiles" ../llvm-bolt/llvm -DLLVM_TARGETS_TO_BUILD="X86;AArch64" -DCMAKE_BUILD_TYPE=Release -DLLVM_ENABLE_ASSERTIONS=ON -DLLVM_ENABLE_PROJECTS="clang;lld;bolt"
> make -j
```

## Build BAT-dump
```bash
> mkdir llvm-project && cd llvm-project
> git clone git@github.com:llvm/llvm-project.git
> mkdir build && cd llvm
> git checkout 2b88298c2ab221228744ca8dba70c2d3bcff593b
> cd ../build
> cmake -G "Unix Makefiles" -DCMAKE_BUILD_TYPE=Release -DLLVM_ENABLE_PROJECTS="clang;compiler-rt;bolt" ../llvm
> make -j
```

## Build llvm-10.0 from source
- download LLVM 10.0 (Source code(tar.gz)) from https://github.com/llvm/llvm-project/releases/tag/llvmorg-10.0.0
- build LLVM (reference: https://llvm.org/docs/GettingStarted.html)
```bash
> wget https://github.com/llvm/llvm-project/archive/refs/tags/llvmorg-10.0.0.tar.gz
> tar -vxf llvmorg-10.0.0.tar.gz
> mv llvmorg-10.0.0 llvm-project && cd llvm-project
> mkdir build && cd build
> cmake -G "Unix Makefiles" -DCMAKE_BUILD_TYPE=Release -DLLVM_ENABLE_PROJECTS="clang;compiler-rt" ../llvm
> make -j
```

## Build & run RPG^2
- Download RPG^2
```bash
> git clone git@github.com:zyuxuan0115/RPG2-public.git
> cd RPG2-public
> export RPG2_PATH=/your/absolute/path/to/pg2_reloc/directory
> make
```
- `make` will produce 1 executables (`tracer`)+ 1 shared library (`inject_prefetch.so`). 
   * If libunwind library is stored in other places instead of `/usr/local/lib`, you also need to edit Makefile and update it to the corresponding path.
   * If libunwind's header files are stored in other places instead of `/usr/local/include`, you also need to edit Makefile and update it to the corresponding path. 
- In the file `config`, specify the absolute path for `nm`,`perf`,`objdump`,`llvm-bolt`,`perf2bolt` and `bat-dump` [^3]
   [^3]: if `nm`,`objdump` and `perf` are already in shell, it's OK that their paths are not specified in `config`. This can be checked by `which nm`, `which objdump` and `which perf`.
- Compile workloads
- (1) compile CRONO workloads with `kill(getppid(), SIGUSR1);` To run pg2, you have to compile CRONO workloads with `kill(getppid(), SIGUSR1)`.
```bash
> cd workloads/CRONO/pagerank_lock
> make
> cd ../../..
```
- (2) compile CRONO workloads without `kill(getppid(), SIGUSR1);` \
To measure the real execution time of CRONO workloads, you have to compile CRONO workloads without `kill(getppid(), SIGUSR1);`\
In `pg2_reloc/workloads/CRONO/Makefile`, delete the `-DSIGNAL`, then run `make` 

- (3) compile AinsworthCGO2017 workloads
```bash
> cd workloads/AinsworthCGO2017/nas-is
> sh compile_x86.sh
> cd ../../..
```
- In `config`, please also specify the commands to run the workload. The example commands are given in the config file. 
   * _Note_: the first argument of the command (a.k.a. the binary being invoked in the command) should be written in its full path. 

- Run rpg^2:
```bash
> ./extract_call_sites
> ./tracer
```

## Miscellaneous (notes about how to debug RPG^2)
In `Makefile`'s `CXXFLAGS`,
- if `-DTIME_MEASUREMENT` flag is added, rpg^2 will print the execution time of code replacement;
- if `-DMEASUREMENT` flag is added, rpg^2 will print metrics such as:  
  * the number of functions on the call stack when target process is paused,
  * the number of functions that are moved by `BOLT`,
  * the number of functions that are in the `BOLT` and original functions.
- if `-DDEBUG_INFO` flag is added, rpg^2 will print debug information such as:
  * the information about detailed behavior of tracer
  * the content in the call stack when the target process is paused
  * `-DDEBUG_INFO` can also be defined in `src/inject_prefetch.hpp`. In this way, the ld_preload library will store all machine code per function it inserted to the target process as a `uint8_t` format array into a file. The file can be found in the `tmp_data_path` you defined in the config file. 
- if `-DDEBUG` flag is added, after code replacement, rpg^2 will first send `SIGSTOP` signal to target process and then resume the target process by `PTRACE_DETACH`. In this way, it allows debugging tools such as `GDB` to attach to the target process and observe what goes wrong after code replacement.


