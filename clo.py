# Pythonic closures

def startswith(prefix):
        """returns a closure which returns true when the passed string matches prefix"""
        return lambda s: s.startswith(prefix)

def dictgetter(vals, err):
        """Create a dictionary lookup function which returns 'unknown {err} {key}'"""
        def getter(key):
                return vals.get(key, 'unknown {0} {1}'.format(err, key))
        return getter

def moduledictgetter(module, prefix, err):
        """Create a mapping function from module IDs to the module constants"""
	mod = __import__(module)
	return dictgetter(dict((getattr(mod,x),x) for x in filter(startswith(prefix), dir(mod))), err)

