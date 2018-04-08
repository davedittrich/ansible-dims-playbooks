shflags: $(DIMS)/src/shflags
	(cd $(DIMS)/src; tar -cf - shflags) | tar -xf -

bats: $(DIMS)/src/bats
	(cd $(DIMS)/src; tar -cf - bats) | tar -xf -

%: force
	        @$(MAKE) -f Makefile $@
force: ;
