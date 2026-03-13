EXECUTABLES=hello gmm ode llsq det

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

bin/gmm: gmm.cpp
	mkdir -p bin
	$(CXX) $(CXXFLAGS) -o $@ gmm.cpp $(LDFLAGS) $(LDLIBS)

bin/ode: ode.cpp
	mkdir -p bin
	$(CXX) $(CXXFLAGS) -o $@ ode.cpp $(LDFLAGS) $(LDLIBS)

bin/llsq: llsq.cpp
	mkdir -p bin
	$(CXX) $(CXXFLAGS) -o $@ llsq.cpp $(LDFLAGS) $(LDLIBS)

bin/det: det.cpp
	mkdir -p bin
	$(CXX) $(CXXFLAGS) -o $@ det.cpp $(LDFLAGS) $(LDLIBS)
