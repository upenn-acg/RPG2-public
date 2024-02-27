/home/zyuxuan/llvm-project-10.0/build/bin/clang -O3 -Wall -no-pie -DFETCHDIST=512 -DSTRIDE isswpf.c -c 
/home/zyuxuan/llvm-project-10.0/build/bin/clang -O3 -Wall -no-pie -DFETCHDIST=512 -DSTRIDE isswpf.o ../nas-common/c_print_results.c ../nas-common/c_timers.c ../nas-common/wtime.c  -o isswpf  -lpthread -lrt -Wl,--emit-relocs

/home/zyuxuan/llvm-project-10.0/build/bin/clang -O3 -Wall -no-pie -DSIGNAL is.c -c 
/home/zyuxuan/llvm-project-10.0/build/bin/clang -O3 -Wall -no-pie -DSIGNAL is.o ../nas-common/c_print_results.c ../nas-common/c_timers.c ../nas-common/wtime.c -o is -lpthread -lrt -Wl,--emit-relocs
