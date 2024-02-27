CXX=/home/zyuxuan/llvm-project-10.0/build/bin/clang++
#CXX=/home/zyuxuan/llvm-17.0/build/bin/clang++
#CXX=/usr/bin/g++
TRGS=pagerank_lock
LIBS=-lpthread -lrt -Wl,--emit-relocs
CXXFLAGS=--std=c++11 -O3 -Wall -no-pie -DSIGNAL
#CXXFLAGS=--std=c++11 -O3 -Wall -no-pie
#CXXFLAGS=-gmlt --std=c++11 -O3 -fdebug-info-for-profiling -Wall -no-pie
#CXXFLAGS=-O3 -fno-align-jumps -fno-align-loops -fno-align-labels -Wall
all: $(TRGS)

pagerank_lock: pagerank_lock.cc
	$(CXX) $(CXXFLAGS) $< -o $@ $(LIBS)

clean:
	rm -f $(TRGS) *.o *.dot
	rm -f file.txt
