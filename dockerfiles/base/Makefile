DOCKERFILES ?= $(shell dirname `pwd`)
include $(DIMS)/etc/Makefile.dims.global
include $(DOCKERFILES)/Makefile.container

#HELP setup - load pre-requisites needed for building Docker image
setup:
	make -f GNUmakefile shflags bats
