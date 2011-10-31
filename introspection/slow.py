# Python introspection to some standard libraries and more
# This is the version which is slow on runtime but faster on init time

import pytino
from pytino import clo
from pytino import introspection

def get(module, prefix, what):
	# This workaround by using a mutable container is somewhat annoying.
	# I want to be able to assign to variables of an outer scope!
	# Also the error which is seen is quite a bit misleading!
	mod = [None]
	def getter(key):
		if not mod[0]:
			mod[0] = __import__(module)
		for x in filter(clo.startswith(prefix), dir(mod[0])):
			if key==getattr(mod[0],x):
				return x
                return 'unknown {0} {1}'.format(module+what, key)
        return getter

introspection._impl(__name__, get)

if __name__ == '__main__':
	print introspection.sockAF(1)
