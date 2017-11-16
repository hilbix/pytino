Python helpers to include as GIT submodules

Use the source.  Or the README.md in other directories.

Also there are short snippets in recipe on how to do a thing.

This Works is placed under the terms of the Copyright Less License,
see file COPYRIGHT.CLL.  USE AT OWN RISK, ABSOLUTELY NO WARRANTY.


log.py: Typical use

	import pytino.log as log
	__LOGLEVEL__ = log.WARNING	# hides logging below this level

	log.sane(__file__, log.ALL)	# done only in __main__

	log.info('not shown')	# above log.ALL, but below __LOGLEVEL__
	log.warn('shown')	# allowed by both
	log.level(log.FATAL)	# changes the level from .sane()
	log.warn('not shown')	# now this is below the loglevel

log.py: Simple logger wrapper (ignore stack from this module):

        # This assumes your main program uses pytino.log
	# If not, __LOGWRAPPER__ = logging does no harm.

        import logging
	__LOGWRAPPER__ = logging

	# Do not have a __LOGLEVEL__ on the caller, as this throws!
	def mylog(*args, **kw):
		logging.log(logging.INFO, ..whatever..)

log.py: Typical logger wrapper:

        import pytino.log as log
	__LOGWRAPPER__ = logging

	# Thanks to xlog(), the calling module can have a __LOGLEVEL__
	def mylog(*args, **kw):
		log.xlog(log.INFO, ..whatever.., exc_info=True)

