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
# #log.setup('name', log.ALL)	# for full debugging
# log.setup('name', log.ERROR)	# default is log.INFO
# log.warn('hello', 'world')	# not shown for log.ERROR
#
# log.twisted()			# if you use twisted
# log.asyncio()			# if you use asyncio (makes logging using async)
#
# In modules:
#
# import pytino.log as log
# __LOGLEVEL__ = log.ERROR
# log.warn(*['suppressed', 'by','__LOGLEVEL__'])
# log.err('this', 'is', 'shown', 'if',loglevel='ERROR',_or_='below')
# Note: Sequence of KWs cannot be maintained!
#
# Also you can do:
#
# from pytino.log import setup as logsetup
#
# log = logsetup('name').info	# logsetup('name',logsetup.ALL) for ALL etc.
# log('whatever')

# ignore the "as", it is to hide away the globals
from __future__ import absolute_import as _absolute_import
from __future__ import print_function as _print_function

import os as _os
import sys as _sys
import time as _time
import logging as _logging


# This is a log wrapper
__LOGWRAPPER__	= _logging

# WTF?  Why is this missing?
__module__	= _sys.modules[__name__]

# Define some constants
_SANEFORMAT	= '%(asctime)s %(levelname)s %(name)s %(module)s:%(lineno)s %(funcName)s %(message)s'
_FULLFORMAT	= '%(asctime)s %(levelname)s %(name)s %(pathname)s:%(lineno)s %(funcName)s %(message)s'
_SANEDATE	= '%Y%m%d-%H%M%S'

# Set some global runtime variables
__DEBUGGING__	= __name__ == '__main__'
_disabled	= False
_level		= None


# missing environment test
def __setup__():	# Do not pollute globals()
	'''
	Thos only runs once when this module is first included.  You cannot call it.
	It sets up everything properly and calls logging.basicConfig() for you.
	If you want something else, you can call logging.basicConfig() before.
	Environment:
		PYTHON_LOG_LEVEL:	either a number (level) or 'DEBUG', 'INFO', etc.
		PYTHON_LOG_FILE:	an additional file to log to.
		PYTHON_LOG_FORMAT:	set your own logging format
		PYTHON_LOG_DEBUG:	use full name to filenames in log and further debugging
	There is a special level 'NONE', which disables logger via this module.
	'''
	# ensure this is called only once
	__module__.__setup__ = lambda: None
	if hasattr(_logging, '__LOGWRAPPER__') and _logging.__LOGWRAPPER__ == _logging: return

	#
	# Below only runs once:
	#

	_logging.addLevelName(NONE, 'NONE')	# sad: this does not define logging.NONE
	_logging.addLevelName(ALL, 'ALL')	# sad: this does not define logging.ALL
	_logging.ALL	= ALL			# WTF? addLevelName() forgets this?
	_logging.NONE	= NONE			# sad: this only works with this module here

	# Now fix some of the most obvious fatal design errors in logging
	# WTF?  Blanks in a column of traditionally blank separated fields?
	# Patch in some underscore, and write it uppercase as other levels.

	if getattr(_logging, '_levelToName', None) and getattr(_logging, '_nameToLevel', None):
		_logging.getLevelName = lambda level: _logging._levelToName.get(level, _logging._nameToLevel.get(level, ("LEVEL_%s" % level)))
	else:
		_logging.getLevelName = lambda level: _logging._levelNames.get(level, ("LEVEL_%s" % level))

	# possibly needed in setup()
	__module__._o_curframe_	= _logging.currentframe

	# Eliminate stackframes from (this and possibly other) wrapper modules
	_logging.__LOGWRAPPER__	= _logging
	_logging.currentframe	= _removeWrapperFrames(_logging.currentframe)
	_logging.Logger._log	= _ignoreNoLoggingException(_logging.Logger._log)

	if _os.getenv('PYTHON_LOG_DEBUG'):
		__module__.__DEBUGGING__	= True

	_logging.basicConfig(datefmt=_SANEDATE, format=_os.getenv('PYTHON_LOG_FORMAT') or __module__.__DEBUGGING__ and _FULLFORMAT or _SANEFORMAT)

	# Why isn't there an ENV var which let us overwrite the level?
	# Why has this to be done by yourself, parsing options or even more crappy?
	lvl	= None
	env	= _os.getenv('PYTHON_LOG_LEVEL')
	if env:
		try:	lvl = int(env)
		except:	lvl = getattr(__module__, env, None)
	if not isinstance(lvl, int):
		lvl	= INFO
	level(lvl)

	# BUG: Timezone is missing in timestamps by default (the ISO8601 isn't ISO8601 compliant)
	# Logging shall always be done in UTC, to be able to compare server times
	_logging.Formatter.converter = _time.gmtime	# stackoverflow.com/questions/6321160

	# Why isn't this the default since Python 0.0?
	# Why does only work for Python 2.7 and above?
	try: _logging.captureWarnings(True)
	except: pass

	env = _os.getenv('PYTHON_LOG_FILE')
	if env:
		_logging.getLogger().addHandler(_logging.FileHandler(env,'a'))

	# inject everything into everything
	# such that even if you get some .info as logging routine,
	# you can still can switch over to .warn etc.
	names = { name:getattr(__module__,name) for name in __module__.__dict__ if not name.startswith('_') }
	for a in names:
		o	= getattr(__module__, a)
		if callable(o):
			for k,v in names.items():
				setattr(o, k, v)


# barely tested
def level(level=None):
	'''
	Get or set the logging level to something else.
	If set to 0 (NONE), logging is entirely disabled.
	If it is lower than a module's __LOGLEVEL__,
	the latter wins on the module scale.
	'''
	if level == NONE or level == 'NONE':
		__module__._disabled	= True
		level			= 99999
	elif level:
		__module__._disabled	= False
	if level:
		# Are we really in Java here?  Pretty looks like it: WTF!
		_logging.getLogger().setLevel(level)
		__module__._level	= level

	return not __module__._disabled and __module__._level or NONE


def levelName(level=None):
	if level is None:
		level	= __module__.level()
	return _logging.getLevelName(level)


def disabled():
	"""
	returns true if logging is disabled
	"""
	return __module__._disabled

# untested
def formatter(form=None):
	'''
	Change the output format.
	Perhaps use in combination of xlog(.., extra={..})
	If new formatter is None or not given, switch back to sane format.
	'''
	if form is None:
		form = _logging.Formatter(_SANEFORMAT, _SANEDATE)
	# This strongly reminds me to the minecraft.forge style:
	_logging.getLogger().setFormatter(form)


def setup(name=None, level=None):
	'''
	From main run:
		log.setup(__file__)
	Optional argument "level" defaults to logging.INFO.
		The default value is only used if not overridden in environment.
		If 0 (NONE), logging (via this module) is entirely disabled.
	'''

	if name is None:
		# try to deduce the correct name from the caller of setup()
		name	= __module__._o_curframe_().f_code.co_filename

	# Zap the 'root' in favor of the set name (why is there no .setName()?)
	_logging.getLogger().name = name
	__module__.level(level)

	# returns the logging module itself
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
	if __module__._disabled: return

#	print(__LOGLEVEL__, s, args, kw)

	# module.__LOGLEVEL__ support hacked in here.
	# This probably only works with modules,
	# which use pytino.log, of course.
	try:
		_logging.log(__LOGLEVEL__, str(s).rstrip(' \t\n\r'), *args, **kw)
#		if __module__.__DEBUGGING__: print('oh, baby, try')
	except _NoLoggingException:
#		if __module__.__DEBUGGING__: print('eye to eye')
		pass


# XXX TODO XXX tested, but incomplete (missing escapes)
def log(level, *args, **kw):
	'''
	Do some logging without thinking about anything.
	All arguments given are just output in the log.
	No hidden pitfalls or similar.
	'''
	if __module__._disabled: return
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
			if not f.f_globals.get('__LOGWRAPPER__', None) is _logging:
				if f.f_globals.get('__LOGLEVEL__', 0) > l > 0:
#					if __module__.__DEBUGGING__: print('hush hush')
					raise _NoLoggingException()
				if same:	c = f
#				if __module__.__DEBUGGING__ and c.f_code: print('@DEBUG@log@', c.f_code.co_filename, file=_sys.stderr)
				return c
			l = f.f_locals.get('__LOGLEVEL__', l)
			p = c
			c = f
			f = f.f_back
		if f is None and not same:
			c = p
		return c
	return wrap


# This can be used as a decorator
def _ignoreNoLoggingException(_log):
	'''
	Wrap a logging function such, that _NoLoggingException is ignored.
	In that case the function just returns without doing anything.
	'''
	def wrap(c, l, s, *args, **kw):
		try:
			_log(c, l, str(s).rstrip(' \t\n\r'), *args, **kw)
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
		a.__LOGWRAPPER__	= _logging

	# Patch in our stackframe hack
	ts.currentframe =	_removeWrapperFrames(ts.currentframe, same=True)

	if args or kw:
		setup(*args, **kw)

	ll("Twisted logging enabled")

	return __module__


def asyncio(*args, **kw):
	'''
	Enable this module for asyncio logging.

	NOT YET READY (logging is blocking)
	'''

	if args or kw:
		setup(*args, **kw)

	ll("AsyncIO logging enabled")

	return __module__


NONE	= 0
ALL	= 1
DEBUG	= _logging.DEBUG
INFO	= _logging.INFO
WARNING	= _logging.WARNING
ERROR	= _logging.ERROR
FATAL	= _logging.FATAL


# And here some convenience wrappers:
# Note that they dump their keywords,
# if you need stackframes etc. use xlog()!
def ll   (*args, **kw):	log(ALL,     *args, **kw)
def debug(*args, **kw):	log(DEBUG,   *args, **kw)
def info (*args, **kw):	__module__.log(__module__.INFO,    *args, **kw)
def warn (*args, **kw):	__module__.log(__module__.WARNING, *args, **kw)
def err  (*args, **kw):	__module__.log(__module__.ERROR,   *args, **kw)
def fatal(*args, **kw):	__module__.log(__module__.FATAL,   *args, **kw)


# Do all the patching stuff, once for a lifetime.
__setup__()


def _test():
	sep	= lambda: print('---------------------------------------------------------')

	# reveal me
	# well, this reveals the innermost function here
	# which is "xlog", but this is for testing only anyway.
	__module__.__LOGWRAPPER__	= None

	log	= fatal

	sep()
	print(log.__dict__)

	sep()
	log.setup()
	print(log.level(), log.levelName(), log.disabled())
	log("this can be seen")

	sep()
	log.setup('test', NONE)
	print(log.level(), log.levelName(), log.disabled())
	log("this cannot be seen")

	sep()


if __name__=='__main__':
	_test()

