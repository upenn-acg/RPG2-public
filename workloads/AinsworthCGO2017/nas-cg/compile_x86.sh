/home/zyuxuan/llvm-project-10.0/build/bin/clang -O3 -Wall -no-pie -DFETCHDIST=16 cgswpf.c -c 
/home/zyuxuan/llvm-project-10.0/build/bin/clang -O3 -Wall -no-pie -DFETCHDIST=16 cgswpf.o ../nas-common/c_print_results.c ../nas-common/c_timers.c ../nas-common/wtime.c -lm ../nas-common/c_randdp.c -o cgswpf  -lpthread -lrt -Wl,--emit-relocs

/home/zyuxuan/llvm-project-10.0/build/bin/clang -O3 -Wall -no-pie -fno-unroll-loops -DSIGNAL cg.c -c 
/home/zyuxuan/llvm-project-10.0/build/bin/clang -O3 -Wall -no-pie -fno-unroll-loops -DSIGNAL cg.o ../nas-common/c_print_results.c ../nas-common/c_timers.c ../nas-common/wtime.c -lm ../nas-common/c_randdp.c -o cg  -lpthread -lrt -Wl,--emit-relocs
