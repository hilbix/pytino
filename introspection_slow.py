# Python introspection to some standard libraries and more
# This is the version which is slow on runtime but faster on init time

from clo import startswith
import introspection_impl

def get(module, prefix, what):
	# This workaround by using a mutable container is somewhat annoying.
	# I want to be able to assign to variables of an outer scope!
	# Also the error which is seen is quite a bit misleading!
	mod = [None]
	def getter(key):
		if not mod[0]:
			mod[0] = __import__(module)
		for x in filter(startswith(prefix), dir(mod[0])):
			if key==getattr(mod[0],x):
				return x
                return 'unknown {0} {1}'.format(module+what, key)
        return getter

introspection_impl._impl(__name__, get)

if __name__ == '__main__':
	# Note that if you do
	# import pytino.introspection_slow
	# this populates these functions into pytino
	# I really have no idea why.
	# __import__('pytino.introspection_slow') gives me the module 'pytino'
	print sockAF(1)
