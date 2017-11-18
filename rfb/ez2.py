#!/usr/bin/env python2
#
# vim:set ts=8:
#
# ez2, because it needs Python2, because "rfb" and pyDes ares not Python3 compliant.
# This here also needs twisted, which is bad.
# Perhaps I will find time to create some ez3 for Python3 without twisted.
#
# Wrapper around RFB library.  Hides all those ugly twisted stuff from you.
#
# This Works is placed under the terms of the Copyright Less License,
# see file COPYRIGHT.CLL.  USE AT OWN RISK, ABSOLUTELY NO WARRANTY.
#
# Prepare:
#	git clone https://github.com/hilbix/python-vnc-viewer.git
#	ln -s python-vnc-viewer/pyDes.py python-vnc-viewer/rfb.py .
#	./ez2.py host port [password]
#
# Usage like:
#
# import pytino.rfb.ez as easyrfb
#
# class myRfb(easyrfb.client):
#	def __init__(self, ..., *args, **kw):
#		easyrfb.client.__init__(self, *args, **kw)
#
#	def whateverfunctionneedsoverrwrite(self, ...):
#		function
#
# myRfb(args, ...).run()
#
# To set another logger than pytino.log.debug:	.logger(...).
# To set another twisted application use:	.application(...).
# To not call twisted twisted.internet.reactor.run() use .run() instead

import os
import sys

try:
	from .. import log
except:
	os.sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
	import pytino.log as log

import twisted
import rfb

def getKeys():
	"""getKeys() returns an unsorted list of arguments, getKey() knows about"""
	return [ s[4:] for s in rfb.__dict__ if s.startswith('KEY_') ]

def getKey(s):
	"""getKey(key) returns truthy Key value if given key is known, false otherwise"""
	s = 'KEY_'+s
	return s in rfb.__dict__ and rfb.__dict__[s]

class FunnelRfbProtocol(rfb.RFBClient):

	def connectionMade(self):
		self.factory.wrap.connectionMade(self)

	def vncConnectionMade(self):
		self.factory.wrap.vncConnectionMade(self)

	def beginUpdate(self):
		self.factory.wrap.beginUpdate(self)

	def updateRectangle(self, x, y, width, height, data):
		self.factory.wrap.updateRectangle(self, x, y, width, height, data)

	def commitUpdate(self, rectangles=None):
		self.factory.wrap.commitUpdate(self, rectangles)

# This just funnels everything to the wrapper
class FunnelRfbFactory(rfb.RFBFactory):
	protocol = FunnelRfbProtocol

	def __init__(self, wrapper, password=None, shared=1):
		self.wrap = wrapper
		rfb.RFBFactory.__init__(self, password, shared)

	def buildProtocol(self, addr):
		return rfb.RFBFactory.buildProtocol(self, addr)

	def clientConnectionLost(self, connector, reason):
		self.wrap.log("connection lost:", reason)
		self.wrap.clientConnectionLost(self, connector, reason)

	def clientConnectionFailed(self, connector, reason):
		self.wrap.log("connection failed:", reason)
		self.wrap.clientConnectionFailed(self, connector, reason)

# Here we can have everything at one place
# Easy and simple as it ought to be!
# With reasonable defaults, ready to use.
class client(object):
	def __init__(self, appname='generic RFB client', host=None, port=None, password=None, shared=None, logger=None):

		if host is None:	host	=     self._preset("EASYRFBHOST", '127.0.0.1')
		if port is None:	port	= int(self._preset("EASYRFBPORT", '5900'), 0)
		if password is None:	password =    self._preset("EASYRFBPASS", None)
		if shared is None:	shared	= int(self._preset("EASYRFBSHARED", '1'), 0)

		self.appname	= appname
		self.control	= False
		self.started	= False
		self.app	= None
		self.log	= logger or log.debug
		self.vnc	= twisted.application.internet.TCPClient(host, port, FunnelRfbFactory(self, password, shared))

	def _preset(self, env, default):
		if env in os.environ and os.environ[env]!='':
			return os.environ[env]
		return default

	def application(self, app):
		self.app = app
		return self

	def logger(self, log):
		self.log	= log
		return self

	def start(self):
		twisted.python.log.PythonLoggingObserver(self.appname.replace(" ","_")).start()
		self.vnc.setServiceParent(twisted.application.service.Application(self.appname))
		self.log("starting service:",self.appname)
		self.vnc.startService()
		self.started = True
		return self

	def stop(self):
		if self.started:
			self.started = False
			self.log("stopping service")
			self.vnc.stopService()
		return self

	def run(self):
		self.start()
		self.log("starting reactor")
		self.control = True
		twisted.internet.reactor.run()
		return self

	def halt(self):
		self.stop()
		if self.control:
			self.control = False
			self.log("stopping reactor")
			twisted.internet.reactor.stop()
		return self

	def clientConnectionFailed(self, factory, connector, reason):
		self.log("connection failed:", reason)
		self.halt()

	def clientConnectionLost(self, factory, connector, reason):
		self.log("connection lost:", reason)
		self.halt()

	def connectionMade(self, vnc):
		self.log("connectionMade")

	def vncConnectionMade(self, vnc):
		self.log("Orig. screen:  %dx%d depth=%d bits_per_pixel=%r bytes_per_pixel=%r" % (vnc.width, vnc.height, vnc.depth, vnc.bpp, vnc.bypp))
		self.log("Desktop name:  %r" % vnc.name)

		vnc.setEncodings([rfb.RAW_ENCODING])
		vnc.setPixelFormat()

		self.log("Screen format: %dx%d depth=%d bits_per_pixel=%r bytes_per_pixel=%r" % (vnc.width, vnc.height, vnc.depth, vnc.bpp, vnc.bypp))

		vnc.framebufferUpdateRequest()

	def beginUpdate(self, vnc):
		self.log("beginUpdate")

	def updateRectangle(self, vnc, x, y, width, height, data):
		self.log("updateRectangle", x, y, width, height)

	def commitUpdate(self, vnc, rectangles=None):
		self.log("commitUpdate", rectangles)
		self.stop()

if __name__=='__main__':
	log.sane(__name__, 1).twisted()

	# host port password
	args = {}
	if len(sys.argv)>1: args["host"    ] = sys.argv[1]
	if len(sys.argv)>2: args["port"    ] = int(sys.argv[2])
	if len(sys.argv)>3: args["password"] = sys.argv[3]
	if len(sys.argv)>4: args["shared"  ] = int(sys.argv[4])
	client(**args).run()

