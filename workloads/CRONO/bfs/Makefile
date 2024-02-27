CXX=/home/zyuxuan/llvm-project-10.0/build/bin/clang++
#CXX=/home/zyuxuan/llvm-17.0/build/bin/clang++
#CXX=/usr/bin/g++
LIBS=-lpthread -lrt -Wl,--emit-relocs
CXXFLAGS=--std=c++11 -O3 -Wall -no-pie -DSIGNAL

TRGS = bfs

#CXXFLAGS = -g --std=c++0x -O3
#CXXFLAGS += -Wall

all: $(TRGS)

bfs: bfs.cc

clean:
	rm -f $(TRGS) *.o *.dot
	rm -f myfile.txt

%: %.cc ;
	$(CXX) $(CXXFLAGS) $< -o $@ $(LIBS)
