# love make

TESTS=log.py

.PHONY:	love
love:	is all

.PHONY:	%
%:
	$(MAKE) -C .. $@

# For python3vim.sh see
# https://raw.githubusercontent.com/hilbix/tino/master/howto/python3vim.sh
.PHONY:	is
is:
	@for a in $(TESTS); do echo "testing $$a:"; python3vim.sh "./$$a" || break; done

clean:
	rm -f *.pyc
	rm -rf __pycache__
