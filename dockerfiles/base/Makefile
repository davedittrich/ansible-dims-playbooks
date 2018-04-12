DOCKERFILES ?= $(shell dirname `pwd`)
include $(DIMS)/etc/Makefile.dims.global
include $(DOCKERFILES)/Makefile.container

#HELP setup - load pre-requisites needed for building Docker image
setup:
	if [ -f GNUmakefile ]; then make -f GNUmakefile shflags bats; fi
	if [ -f setup.sh ]; then bash setup.sh; fi
