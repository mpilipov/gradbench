EXECUTABLES=hello gmm lstm ba ht kmeans ode llsq det lse

include ../../cpp/common.mk

CXXFLAGS += -I"C:/Users/Michael/Downloads/gradbench"
CXXFLAGS += -I"C:/Users/Michael/Desktop/thesis25/CoDiPack-master/include"
CXXFLAGS += -DCODI_ForcedInlines=1

ifdef CODI_TYPE
  CXXFLAGS+=-DCODI_TYPE=$(CODI_TYPE)
endif
