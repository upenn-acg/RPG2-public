cd src
#clang -O3 npj2epb.c -Xclang -load -Xclang ../../../package/plugin-llvm-sw-prefetch-pass/lib/SwPrefetchPass.so -c -S -emit-llvm 
#clang -O3 npj2epb.ll -c 
#clang -O3 npj2epb.o main.c generator.c genzipf.c perf_counters.c cpu_mapping.c parallel_radix_join.c -lpthread -lm -std=c99  -o bin/x86/hj2-auto
#clang -O3 npj2epb.c -Xclang -load -Xclang ../../../package/plugin-llvm-sw-prefetch-no-strides-pass/lib/SwPrefetchPass_noStrides.so -c -S -emit-llvm 
#clang -O3 npj2epb.ll -c 
#clang -O3 npj2epb.o main.c generator.c genzipf.c perf_counters.c cpu_mapping.c parallel_radix_join.c -lpthread -lm -std=c99  -o bin/x86/hj2-auto-nostride
/home/zyuxuan/llvm-project-10.0/build/bin/clang -O3 -no-pie npj2epb.c -c 
/home/zyuxuan/llvm-project-10.0/build/bin/clang -O3 -no-pie npj2epb.o main.c generator.c genzipf.c perf_counters.c cpu_mapping.c parallel_radix_join.c -lpthread -lm -std=c99  -o npj2epb -Wl,--emit-relocs
/home/zyuxuan/llvm-project-10.0/build/bin/clang -O3 -no-pie npj2epbsw.c -DFETCHDIST=64 -DSTRIDE -c 
/home/zyuxuan/llvm-project-10.0/build/bin/clang -O3 -no-pie npj2epbsw.o main.c generator.c genzipf.c perf_counters.c cpu_mapping.c parallel_radix_join.c -lpthread -lm -std=c99  -o npj2epbsw -Wl,--emit-relocs

/home/zyuxuan/llvm-project-10.0/build/bin/clang -O3 -no-pie npj8epb.c -c 
/home/zyuxuan/llvm-project-10.0/build/bin/clang -O3 -no-pie npj8epb.o main.c generator.c genzipf.c perf_counters.c cpu_mapping.c parallel_radix_join.c -lpthread -lm -std=c99  -o npj8epb -Wl,--emit-relocs
/home/zyuxuan/llvm-project-10.0/build/bin/clang -O3 -no-pie npj8epbsw.c -DFETCHDIST=64 -DSTRIDE -c 
/home/zyuxuan/llvm-project-10.0/build/bin/clang -O3 -no-pie npj8epbsw.o main.c generator.c genzipf.c perf_counters.c cpu_mapping.c parallel_radix_join.c -lpthread -lm -std=c99  -o npj8epbsw -Wl,--emit-relocs
