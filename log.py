#
# Sorry, logging in Pythin is far too complex
#
# This is a sane logging handler:
# - Allows to specify the logging level in the environment (0 is DEBUG, 99 is off, probably)
# - Allows to specify the logging filename in the environment as well.
# Sets up logging with a sane UTC timestamp which is easy to read across different systems.

import pytino.introspection.slow
import logging
import time
import os

def sane(name, level=None):
	'''
	call with __file__ from __main__.
	optional log level defaults to INFO
	'''
	# Why isn't there an ENV var which let us overwrite the level?
	# Why has this be done by yourself parsing options or even more crappy things?
	env = os.getenv('PYTHON_LOG_LEVEL')
	if env:
		try:	level = int(env)
		except:	level = getattr(logging, env, None)
	if not isinstance(level, int):
		level	= logging.INFO
	logging.basicConfig(level=level, format='%(asctime)s %(name)s %(levelname)-8s %(message)s', datefmt='%Y%m%d-%H%M%S')

	# BUG: Timezone is missing in timestamps by default (the ISO8601 isn't ISO8601 compliant)
	# Logging shall always be done in UTC, to be able to compare server times
	logging.Formatter.converter = time.gmtime  # stackoverflow.com/questions/6321160

	# Why isn't this the default since Python 0.0?
	# Why does only work for Python 2.7 and above?
	try: logging.captureWarnings(True)
	except: pass

	# Zap the 'root' in favor of the main script's filename
	logging.getLogger().name = name

	env = os.getenv('PYTHON_LOG_FILE')
	if env:
		logging.getLogger().addHandler(logging.FileHandler(env,'a'))

	return logging
