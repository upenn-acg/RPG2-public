CXX=/home/zyuxuan/llvm-project-10.0/build/bin/clang++
#CXX=/home/zyuxuan/llvm-17.0/build/bin/clang++
#CXX=/usr/bin/g++
LIBS=-lpthread -lrt -Wl,--emit-relocs
CXXFLAGS=--std=c++11 -O3 -Wall -no-pie

TRGS = dfs

all: $(TRGS)

dfs: dfs.cc

clean:
	rm -f $(TRGS) *.o *.dot

%: %.cc ;
	$(CXX) $(CXXFLAGS) $< -o $@ $(LIBS)
