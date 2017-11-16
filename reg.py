# Registry for module constants with additional info
#
# vim:set ts=8:

import re
import itertools
import pytino.log as log

__LOGLEVEL__ = log.ALL+1
log = log.ll

_VALIDNAME	= re.compile(r"^[a-z][a-z0-9_]*$", re.IGNORECASE)

class Keeper(dict):
	@staticmethod
	def _key(idx):
		return int(idx)

	def __setitem__(self, idx, val):
		raise RuntimeError('__setitem__ cannot be called directly')

	def __getitem__(self, idx):
		try:
			return super().__getitem__(self._key(idx))
		except KeyError:
			return None

	def get(self, idx):
		idx = self._key(idx)
		try:
			return super().__getitem__(idx)
		except KeyError:
			val	= dict()
			super().__setitem__(idx, val)
			return val

class Reg:
	def __init__(self, *args):
		self.__add__(*args)

	@staticmethod
	def _id(name):
		name	= str(name)
		if not _VALIDNAME.match(name):
			raise SyntaxError('{} is not a valid name'.format(name))
		return name

	@classmethod
	def _reg(cls, data): pass

	@classmethod
	def __add__(cls, nr, name, info=None, *args, **kw):
		if not hasattr(cls, '_keep'):
			cls._keep = cls._keeper()

		id	= cls._id(cls.__name__+'_'+name)
		if id in cls._glob and cls._glob[id]!=nr:
			raise RuntimeError('{} already defined differently on module level'.format(id))
		cls._glob[id] = nr

		if not hasattr(cls, name):
			setattr(cls, name, nr)

		elif getattr(cls, name)!=nr:
			raise RuntimeError('{}: Redefined constant to {} (is {})'.format(name, nr, getattr(cls, name)))

		data	= { 'nr':nr, 'name':name, 'info':info }
		cls._reg(data, *args, **kw)

		x = cls._keep.get(nr)
		for a in data:
			if not a in x:
				x[a] = data[a]
				log(id, a, data[a])
			elif x[a] != data[a]:
				raise RuntimeError('{}: Redefined property: {} = {} (was {})'.format(name, a, data[a], x[a]))

	@classmethod
	def get(cls, nr): return cls._get(nr)
	@classmethod
	def _get(cls, nr):
		return cls._keep.get(nr)

	@classmethod
	def gets(cls, name, *args, **kw): return cls._gets(name, *args, **kw)
	@classmethod
	def _gets(cls, name, *args, **kw):
		try:
			return cls._get(getattr(cls, cls._id(name)))
		except AttributeError:
			# We do not accept kw + args
			if kw:
				if len(args)==0:
					return kw
			elif len(args)==1:
				return args[0]
			elif len(args):
				return dict(itertools.zip_longest(*[iter(args)]*2))
			raise


# I tried to make this a function,
# but I failed for unknown reason.
class Registry():
	"""
		reg	= reg.Registry(globals())
		class My(reg.Fn):	pass
		My(1, "DEBUG", "Debug setting", debugging)

		This populates class My with My.DEBUG=1, and
		the current module (globals) with My_DEBUG=1.
		It also keeps the metadata around, like:
			My.get(My.Debug).fn(args..)
	"""
	def __init__(self, glob={}, keeper=Keeper, base=Reg):
		class Reg(base):
			_glob	= glob
			_keeper	= keeper

		class Fn(Reg):
			@classmethod
			def _fn(cls, data): pass

			@classmethod
			def _reg(cls, data, fn=None, *args, **kw):
				data['fn']	= fn
				cls._fn(data, *args, **kw)

		self.Reg	= Reg
		self.Fn		= Fn

