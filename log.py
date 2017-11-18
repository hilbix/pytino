#
# Sane, easy and straightforward logging for Python
#
# vim:set ts=8:
#
# This Works is placed under the terms of the Copyright Less License,
# see file COPYRIGHT.CLL.  USE AT OWN RISK, ABSOLUTELY NO WARRANTY.
#
# Sorry, builtin logging in Python is far too complex.
# There must not be the need for to take care about logging.
# This means, too, do not use `{}` in logging at all!
# Just plain dump, what's given, and let the caller sort things out.
#
# This is a hopefully sane logging handler:
# - Allows to specify the logging level in the environment
# - Allows to specify the logging filename in the environment as well
# - Use UTC timestamp on all systems to make it easy to compare logs
#
# In __main__:
#
# import pytino.log as log
# #log.sane('name', log.ALL)	# for full debugging
# log.sane('name', log.ERROR)	# default is log.INFO
# log.warn('hello', 'world')	# not shown for log.ERROR
#
# log.twisted()			# if you use twisted
#
# In modules:
#
# import pytino.log as log
# __LOGLEVEL__ = log.ERROR
# log.warn(*['suppressed', 'by','__LOGLEVEL__'])
# log.err('this', 'is', 'shown', 'if',loglevel='ERROR',_or_='below')
# Note: Sequence of KWs cannot be maintained!

from __future__ import print_function

import os
import sys
import time
import logging

# This is a log wrapper
__LOGWRAPPER__	= logging

disabled = False

# WTF?  Why is this missing?
__module__ = sys.modules[__name__]

_SANEFORMAT	= '%(asctime)s %(name)s %(filename)s:%(lineno)s %(funcName)s %(levelname)s %(message)s'
_SANEDATE	= '%Y%m%d-%H%M%S'


# missing environment test
def __setup__():	# Do not pollute globals()
	'''
	Only runs once when this module is first included.
	It sets up everything properly and calls logging.basicConfig() for you.
	If you want something else, you can call logging.basicConfig() before.
	Environment:
		PYTHON_LOG_LEVEL: either a number (level) or 'DEBUG', 'INFO', etc.
		PYTHON_LOG_FILE: an additional file to log to.
	There is a special level 'NONE', which disables logger via this module.
	'''
	__module__.__setup__ = lambda: None
	if hasattr(logging, '__LOGWRAPPER__') and logging.__LOGWRAPPER__ == logging: return

	#
	# Below only runs once:
	#

	logging.addLevelName(1, 'ALL')	# sad: this does not define logging.ALL
	logging.ALL	= 1

	# Now fix some of the most obvious fatal design errors in logging
	# WTF?  Blanks in a column of traditionally blank separated fields?
	# Patch in some underscore, and write it uppercase as other levels.

	if getattr(logging, '_levelToName', None) and getattr(logging, '_nameToLevel', None):
		logging.getLevelName = lambda level: logging._levelToName.get(level, logging._nameToLevel.get(level, ("LEVEL_%s" % level)))
	else:
		logging.getLevelName = lambda level: logging._levelNames.get(level, ("LEVEL_%s" % level))

	# Eliminate stackframes from (this and possibly other) wrapper modules
	logging.__LOGWRAPPER__	= logging
	logging.currentframe	= _removeWrapperFrames(logging.currentframe)
	logging.Logger._log	= _ignoreNoLoggingException(logging.Logger._log)

	logging.basicConfig(format=_SANEFORMAT, datefmt=_SANEDATE)

	# Why isn't there an ENV var which let us overwrite the level?
	# Why has this to be done by yourself, parsing options or even more crappy?
	lvl	= None
	env	= os.getenv('PYTHON_LOG_LEVEL')
	if env:
		try:	lvl = int(env)
		except:	lvl = getattr(__module__, env, None)
	if not isinstance(lvl, int):
		lvl	= INFO
	level(lvl)

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


# barely tested
def level(level):
	'''
	Set the logging level to something else.
	If set to 0 (NONE), logging is entirely disabled.
	If it is lower than a module's __LOGLEVEL__,
	the latter wins on the module scale.
	'''
	if level == NONE or level == 'NONE':
		disabled	= True
		level		= 99
	elif level:
		disabled	= False
	if level:
		# Are we really in Java here?  Pretty looks like it: WTF!
		logging.getLogger().setLevel(level)


# untested
def formatter(form=None):
	'''
	Change the output format.
	Perhaps use in combination of xlog(.., extra={..})
	If new formatter is None or not given, switch back to sane format.
	'''
	if form is None:
		form = logging.Formatter(_SANEFORMAT, _SANEDATE)
	# This strongly reminds me to the minecraft.forge style:
	logging.getLogger().setFormatter(form)


def sane(name, level=None):
	'''
	From main run:
		log.sane(__file__)
	Optional argument "level" defaults to logging.INFO.
		The default value is only used if not overridden in environment.
		If 0 (NONE), logging (via this module) is entirely disabled.
	'''
	# Zap the 'root' in favor of the set name (why is there no .setName()?)
	logging.getLogger().name = name
	__module__.level(level)

	return __module__


# Only used internally, to allow to hack a module's __LOGLEVEL__
class _NoLoggingException(Exception):	pass

# Not tested with kw yet
def xlog(__LOGLEVEL__, s, *args, **kw):
	'''
	Use this, if you cannot use log() use xlog() instead of logging.log()!
	It is a wrapper around logging.log() with the same arguments:
		exc_info   = True: print exception information
		exc_info   = sys.exc_info(): print that info
		stack_info = True: print stack info
		extra = { .. }: Extra values which can be used in logformat
	For more see:
		https://docs.python.org/3/library/logging.html#logging.log
	'''
	if disabled: return

	# module.__LOGLEVEL__ support hacked in here.
	# This probably only works with modules,
	# which use pytino.log, of course.
	try:
		logging.log(__LOGLEVEL__, str(s).rstrip(' \t\n\r'), *args, **kw)
	except _NoLoggingException:
		pass


# XXX TODO XXX tested, but incomplete (missing escapes)
def log(level, *args, **kw):
	'''
	Do some logging without thinking about anything.
	All arguments given are just output in the log.
	No hidden pitfalls or similar.
	'''
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
	# XXX TODO XXX
	# Here be Dragons:
	# We need some standard escaping here
	# to allow easy parsing with 3rd party tools
	# in future
	xlog(level, "%s", ' '.join(j).rstrip(' \t\n\r'))


# This could be improved by re-implementing logging.Logger.findCaller()
# However I do not like that, as this is very likely to change.
# Here we just wrap the currentframe, which should be relatively safe.
def _removeWrapperFrames(currentframe, same=True):
	"""
	ignore the stack for modules, which have a property
		__LOGWRAPPER__ = logging
	This is totally safe, because who else would do this?

	Also in modules using this logger, you can set
		__LOGLEVEL__ = N
	to skip all output below this minimal global level,
	such that full debugging needs to be enabled on the module level with
		modulename.__LOGLEVEL__ = 0
	for the case this is needed.
	(However this comes with a performance penalty at low debug levels.)
	"""

	def wrap(*args, **kw):
		c	= currentframe(*args, **kw)
		p	= c
		f	= c
		l	= 0
		while not f is None:
			if not f.f_globals.get('__LOGWRAPPER__', None) is logging:
				if f.f_globals.get('__LOGLEVEL__', 0) > l > 0:
					raise _NoLoggingException()
				if same:	c = f
#				if __module__.__DEBUGGING__ and c.f_code:
#					print('@DEBUG@log@', c.f_code.co_filename, file=sys.stderr)
				return c
			l = f.f_locals.get('__LOGLEVEL__', l)
			p = c
			c = f
			f = f.f_back
		if f is None and not same:
			c = p
		return c
	return wrap


def _ignoreNoLoggingException(_log):
	'''
	Wrap a logging function such, that _NoLoggingException is ignored.
	In that case the function just returns without doing anything.
	'''
	def wrap(c, s, *args, **kw):
		try:
			_log(c, str(s).rstrip(' \t\n\r'), *args, **kw)
		except _NoLoggingException:
			pass
	return wrap


# Currently only tested with Python2
def twisted(*args, **kw):
	'''
	Enable this module for twisted logging,
	including patches to improve the output.
	Please beware as twisted is not prepared for this,
	because twisted assumes, logging is nonblocking,
	but python standard logging might block,
	depending on the configuration.

	You must not have touched twisted.logging before,
	else it might get the wrong currentframe().

	Currently no workaround is known by me, see my (Tino's) comment at
	https://stackoverflow.com/a/2493725
	'''

	import twisted.logger		as t0
	import twisted.logger._legacy	as t1
	import twisted.logger._logger	as t2
	import twisted.logger._observer	as t3
	import twisted.logger._stdlib	as ts	# must be: t4=_stdlib
	import twisted.python.log	as p0
	import twisted.python.threadable as p1

	if hasattr(t0, '__LOGWRAPPER__'):	return	# looks like already patched

	# Ignore all those in logging
	for a in (t0, t1, t2, t3, ts, p0, p1):
		a.__LOGWRAPPER__	= logging

	# Patch in our stackframe hack
	ts.currentframe =	_removeWrapperFrames(ts.currentframe, same=True)

	if args or kw:
		sane(*args, **kw)

	ll("Twisted logging enabled")

	return __module__


NONE	= 0
ALL	= 1
DEBUG	= logging.DEBUG
INFO	= logging.INFO
WARNING	= logging.WARNING
ERROR	= logging.ERROR
FATAL	= logging.FATAL


# And here some convenience wrappers:
# Note that they dump their keywords,
# if you need stackframes etc. use xlog()!
def ll   (*args, **kw):	log(ALL,     *args, **kw)
def debug(*args, **kw):	log(DEBUG,   *args, **kw)
def info (*args, **kw):	log(INFO,    *args, **kw)
def warn (*args, **kw):	log(WARNING, *args, **kw)
def err  (*args, **kw):	log(ERROR,   *args, **kw)
def fatal(*args, **kw):	log(FATAL,   *args, **kw)


# Do all the patching stuff, once for a lifetime.
__setup__()

