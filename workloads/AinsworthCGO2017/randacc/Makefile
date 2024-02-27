CC=/home/zyuxuan/llvm-project-10.0/build/bin/clang
#CC=gcc
LIBS=-lpthread -lrt -Wl,--emit-relocs
CFLAGS=-O3 -Wall -no-pie -DFETCHDIST=32 -DSIGNAL -fno-unroll-loops
#CFLAGS=-O3 -Wall -no-pie -DFETCHDIST=32 -fno-unroll-loops

TRGS = randacc randaccswpf randacc_orig

##BOOST_PATH = /run/pkg/boost-/1.53.0-gcc_4.7.3

##BOOST_FLAGS = -I$(BOOST_PATH)/include -L$(BOOST_PATH)/lib -lboost_graph

all: $(TRGS)

randacc: randacc.c

randaccswpf: randaccswpf.c

randacc_orig: randacc_orig.c

clean:
	rm -f $(TRGS) *.o *.dot

%: %.c ;
	$(CC) $(CFLAGS) $< -o $@ $(LIBS)
