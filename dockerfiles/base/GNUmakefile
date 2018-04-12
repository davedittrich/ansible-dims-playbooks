shflags:
	if [ -f $(DIMS)/src/shflags ]; then \
		tar -C $(DIMS)/src -cf - shflags | tar -xf -; \
	else \
		git clone https://github.com/kward/shflags; \
	fi

bats:
	if [ -f $(DIMS)/src/bats ]; then \
		tar -C $(DIMS)/src -cf - bats | tar -xf -; \
	else \
		git clone https://github.com/sstephenson/bats; \
	fi

%: force
	        @$(MAKE) -f Makefile $@
force: ;
