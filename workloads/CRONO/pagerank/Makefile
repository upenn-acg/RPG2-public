CXX=/home/zyuxuan/llvm-project-10.0/build/bin/clang++
TRGS=pagerank_lock
LIBS=-lpthread -lrt -Wl,--emit-relocs
CXXFLAGS=-gmlt --std=c++11 -O3 -fdebug-info-for-profiling -Wall

all: $(TRGS)

pagerank: pagerank.cc

clean:
	rm -f $(TRGS) *.o *.dot
	rm -f file.txt

%: %.cc ;
	$(CXX) $(CXXFLAGS) $< -o $@ $(LIBS)
