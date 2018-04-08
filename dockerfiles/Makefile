# Makefile
#
# This Makefile is used to set up Docker image creation directories
# with a helper Makefile and other standard files for consistently
# creating Docker images for DIMS components.

CONTAINERS=$(shell find * -name Dockerfile -exec dirname {} ';')
.PHONY: all
all:
	@for container in $(CONTAINERS) \
	 do \
		@echo "[+] Installing $$container/Makefile"; \
	 	cp Makefile.container $$container/Makefile; \
	 done
