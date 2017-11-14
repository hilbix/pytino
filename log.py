#
# Sorry, logging in Python is far too complex.
# There must not be the need for to take care about logging.
# This means, too, do not use `{}` in logging at all!
# Just plain dump, what's given, and let the caller sort things out.
#
# This is a sane logging handler:
# - Allows to specify the logging level in the environment
# - Allows to specify the logging filename in the environment as well
# - Use UTC timestamp on all systems to make it easy to compare logs

import os
import sys
import time
import logging

# This is a log wrapper
__LOGWRAPPER__	= logging

disabled= False

# WTF?  Why is this missing?
__module__ = sys.modules[__name__]

def __setup__():	# Do not pollute globals()
	# Why isn't there an ENV var which let us overwrite the level?
	# Why has this be done by yourself parsing options or even more crappy things?
	level	= INFO
	env	= os.getenv('PYTHON_LOG_LEVEL')
	if env:
		try:	level = int(env)
		except:	level = getattr(__module__, env, None)
	if not isinstance(level, int):
		level	= logging.INFO
	logging.basicConfig(level=level, format='%(asctime)s %(name)s %(filename)s %(funcName)s %(levelname)s %(message)s', datefmt='%Y%m%d-%H%M%S')

	# BUG: Timezone is missing in timestamps by default (the ISO8601 isn't ISO8601 compliant)
	# Logging shall always be done in UTC, to be able to compare server times
	logging.Formatter.converter = time.gmtime  # stackoverflow.com/questions/6321160

	# Why isn't this the default since Python 0.0?
	# Why does only work for Python 2.7 and above?
	try: logging.captureWarnings(True)
	except: pass

	env = os.getenv('PYTHON_LOG_FILE')
	if env:
		logging.getLogger().addHandler(logging.FileHandler(env,'a'))

def level(level):
	if level == NONE:
		disabled	= True
	elif level>0:
		disabled	= False
		# Are we really in Java here?  Pretty looks like it: WTF!
		logging.getLogger().setLevel(level)

def sane(name, level=None):
	'''
	From main run:
		log.sane(__file__)
	Optional argument "level" defaults to logging.INFO.
		The default value is only used if not overridden in environment.
	Environment:
		PYTHON_LOG_LEVEL either a number (level) or 'DEBUG', 'INFO', etc.
		PYTHON_LOG_FILE is an additional file to log to.
	There is a special level 'DISABLED', which disables the logger.
	'''
	# Zap the 'root' in favor of the set name (why is there no .setName()?)
	logging.getLogger().name = name
	__module__.level(level)

	return __module__

# This is the correct way of logging, as it must be:
# DO NOT THINK ABOUT ANYTHING.  Just do it.  Period.
def log(level, *args, **kw):
	if disabled: return
	j = []
	for v in args:
		try:
			j.append(str(v))
		except Exception as e:
			j.append('(exception '+str(e)+')')
	for k,v in kw.items():
		try:
			j.append(str(k)+'='+str(v))
		except Exception as e:
			j.append('(exception '+str(e)+')')

	logging.log(level, "%s", ' '.join(j))


# This could be improved by re-implementing logging.Logger.findCaller()
# However I do not like that, as this is very likely to change.
# Here we just wrap the currentframe, which should be relatively safe.
def removeWrapperFrames(currentframe):
	"""
	ignore the stack for modules, which have a property
		__LOGWRAPPER__ = logging
	This is totally safe, because who else would do this?
	"""

	# This is way faster than the solution found in logging.
	def wrap():
		c	= currentframe()
		f	= c
		while f is not None:
			if not f.f_globals.get('__LOGWRAPPER__', None) is logging:
				return c
			c = f
			f = f.f_back
		return c
	return wrap

NONE	= 0
ALL	= 1
#logging.addLevelName(1, 'ALL')	# this does not define logging.ALL as it should
DEBUG	= logging.DEBUG
INFO	= logging.INFO
WARNING	= logging.WARNING
ERROR	= logging.ERROR
FATAL	= logging.FATAL

def ll   (*args, **kw):	log(ALL,     *args, **kw)
def debug(*args, **kw):	log(DEBUG,   *args, **kw)
def info (*args, **kw):	log(INFO,    *args, **kw)
def warn (*args, **kw):	log(WARNING, *args, **kw)
def err  (*args, **kw):	log(ERROR,   *args, **kw)
def fatal(*args, **kw):	log(FATAL,   *args, **kw)

# Now fix some of the most obvious fatal design errors in logging

# WTF?  Blanks in a column of traditionally blank separated fields?  NO WAY!  FIX!
logging.getLevelName = lambda level: logging._levelToName.get(level, logging._nameToLevel.get(level, ("LEVEL_%s" % level)))

# Eliminate stackframes from wrapper modules
logging.__LOGWRAPPER__ = logging
logging.currentframe = removeWrapperFrames(logging.currentframe)

__setup__()

