#
# Basic idea see https://stackoverflow.caom/a/242531
#
# This can be used as follows:
#
# In your script just do a:
#	import pytino.debug
# or without modifying your script:
#	ln -s lib/pytino/debug.py .
#	python3 -m debug ./script.py

from __future__ import absolute_import

import os
import sys

try:
	import pudb
	def debug(etype, value, tb):
		pudb.post_mortem(tb, etype, value)
#	def main(args):
#		import pudb.run
#		sys.argv	= ['--pre-run=c', '--'] + args
#		pudb.run.main()


except ImportError:

	import pdb
	import traceback
	def debug(etype, value, tb):
		traceback.print_exception(etype, value, tb)
		pdb.post_mortem(tb)
#	def main(args):
#		sys.argv	= ['--command', 'c', '--'] + args
#		pass


orig	= sys.excepthook
stderr	= sys.stderr
if stderr.isatty():
	sys.excepthook	= debug

def runscript(args, script_file=None, globals_ = dict(__name__="__main__"), locals_ = None):
	"""
	Execute a script in it's own context.

	script_filename is optional, taken from args[0]

	The default context is something like it's own global environment,
	executing the script as if it were '__main__'.
	"""
	if script_file is None:
		try:
			script_file	= args[0]
		except IndexError:
			raise TypeError('missing argument script_file: empty arguments')

	# Hooray, reimplement the wheel, in quadratic form

	globals_['__file__']	= script_file

	if locals_ is None:
		locals_	= globals_

	sys.path[0]	= os.path.dirname(script_file)
	sys.argv	= args

	with open(script_file) as f:
		code	= compile(f.read(), script_file, 'exec')
	exec(code, globals_, locals_)

if __name__ == '__main__':
	runscript(sys.argv[1:])

