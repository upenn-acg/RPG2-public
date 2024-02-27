CXX=/home/zyuxuan/llvm-project-10.0/build/bin/clang++
#CXX=/home/zyuxuan/llvm-17.0/build/bin/clang++
#CXX=/usr/bin/g++
LIBS=-lpthread -lrt -Wl,--emit-relocs
CXXFLAGS=--std=c++11 -O3 -Wall -no-pie
TRGS = bc_non_partitioned

##BOOST_PATH = /run/pkg/boost-/1.53.0-gcc_4.7.3

##BOOST_FLAGS = -I$(BOOST_PATH)/include -L$(BOOST_PATH)/lib -lboost_graph

CXXFLAGS = -g --std=c++0x -O3
CXXFLAGS += -Wall -Werror

all: $(TRGS)

bc_non_partitioned: bc_non_partitioned.cc

##boost_dijk_real: boost_dijk_real.cc

clean:
	rm -f $(TRGS) *.o *.dot

%: %.cc ;
	$(CXX) $(CXXFLAGS) $< -o $@ $(LIBS)
