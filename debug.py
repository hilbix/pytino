#
# Basic idea see https://stackoverflow.com/a/242531
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

def runscript(argv, script_file=None, name='__main__', local=None):
	"""
	Execute a script in it's own context as if it were __main__:

	- script_filename is taken from argv[0] if not given
	- name defaults to '__main__'
	- local defaults to the module globals

	Note that this only cannot be used in parallel,
	as it temporarily overrides following entries in sys:

	- sys.modules[name] becomes the executed module
	- sys.path[0] is set to the script's (relative) directory
	- sys.argv is set to the given argv

	Returns tuple (module, code)
	"""
	# determine script
	if script_file is None:
		try:
			script_file	= argv[0]
		except IndexError:
			raise TypeError('missing argument script_file: empty arguments')

	# load script

	with open(script_file) as f:
		code	= compile(f.read(), script_file, 'exec', dont_inherit=True)

	# Hooray, reimplement the wheel, in quadratic form
	#
	# Does somebody know some better way?
	# There shall be nearly no difference of a script
	# when run as
	#	python ./script.py
	# and:
	#	python -m debug ./script.py

	# Create a module to run in.
	# This is the wrong way, but compatible to Python2/3
	# Else we must do this with some error prone and
	# extremely bloated headache bearing code variants
	# for each and every Python version.
	mod			= sys.__class__(name)

	# Now take the globals from the module
	glob			= mod.__dict__
	name			= glob['__name__']

	# Set the __main__ related standard variables
	glob['__file__']	= script_file
	glob['__cached__']	= None
	# No good idea what to do with loader.
	# According to docs, __loader__ should be Null.
	# However, python3.3 sets it to some SourceFileLoader
	# Leave it untouched (None) for now.

	# save the old environment
	oargv			= sys.argv
	opath			= sys.path[0]
	omod			= sys.modules.get(name)

	# store the runtime environment
	sys.modules[name]	= mod
	sys.path[0]		= os.path.dirname(script_file)
	sys.argv		= argv

	# This now is run under debugger control.
	# Hence we do not want to catch exception here.
	exec(code, glob, local is None and glob or local)

	# restore the runtime environment to the original state
	sys.argv		= oargv
	sys.path[0]		= opath
	if omod is None:
		del sys.modules[name]
	else:
		sys.modules[name]	= omod

	# return what was executed for post mortem analysis
	return (mod, code)

if __name__ == '__main__':
	runscript(sys.argv[1:])

