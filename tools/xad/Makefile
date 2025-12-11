EXECUTABLES=hello

# Connecting the common makefile
include ../../cpp/common.mk

# compilation flags
# specifying path to the XAD headers
override CXXFLAGS += -std=c++17 -O3 -march=native -I/opt/xad-install/include

# Linking flags
# specifying path to the XAD library
override LDFLAGS += -L/opt/xad-install/lib
override LDLIBS += -lxad

# main building rule
bin/hello: hello.cpp
	mkdir -p bin
	$(CXX) $(CXXFLAGS) -o $@ hello.cpp $(LDFLAGS) $(LDLIBS)
