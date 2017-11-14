# WiP: SFTP definitions
#
# vim:set ts=8:
# see https://github.com/openssh/openssh-portable/blob/master/sftp.h

_VERSION	= 3

import pytino.reg

_reg = pytino.reg.Registry(globals())

class RWF(_reg.Reg):
	@classmethod
	def _reg(cls, data, read, write, fn=None):
		data['read']	= read
		data['write']	= write
		data['fn']	= fn

class RX(RWF):	pass	# client
class TX(RWF):	pass	# server
    #  Constant		Debug			Read	Write
RX( 0, "INIT",		'init',			False,	False,	);
TX( 1, "VERSION",	'version',		False,	False,	);
RX( 2, "OPEN",		'open',			True,	True,	);
RX( 3, "CLOSE",		'close',		False,	False,	);
RX( 4, "READ",		'read',			True,	False,	);
RX( 5, "WRITE",		'write',		False,	True,	);
RX( 6, "LSTAT",		'lstat',		True,	False,	);
RX( 7, "FSTAT",		'fstat',		True,	False,	);
RX( 8, "SETSTAT",	'setstat',		False,	False,	);
RX( 9, "FSETSTAT",	'fsetstat',		False,	False,	);
RX(10, "OPENDIR",	'opendir',		True,	False,	);
RX(11, "READDIR",	'readdir',		True,	False,	);
RX(12, "REMOVE",	'remove',		False,	True,	);
RX(13, "MKDIR",		'mkdir',		False,	True,	);
RX(14, "RMDIR",		'rmdir',		False,	True,	);
RX(15, "REALPATH",	'realpath',		True,	False,	);
RX(16, "STAT",		'stat',			True,	False,	);
RX(17, "RENAME",	'rename',		False,	True,	);
RX(18, "READLINK",	'readlink',		True,	False,	);
RX(19, "SYMLINK",	'symlink',		False,	True,	);

TX(101, "STATUS",	'status',		False,	False,	);
TX(102, "HANDLE",	'handle',		False,	False,	);
TX(103, "DATA",		'data',			False,	False,	);
TX(104, "NAME",		'name',			False,	False,	);
TX(105, "ATTRS",	'attributes',		True,	False,	);
      
TX(200, "EXT",		'extended',		False,	False,	);
TX(201, "EXT_REPLY",	'extended_reply',	False,	False,	);

class AT(_reg.Reg):	pass
AT(0x00000001,	"SIZE",		);
AT(0x00000002,	"UIDGID",	);
AT(0x00000004,	"PERM",		);
AT(0x00000008,	"ACM_TIME",	);
AT(0x80000000,	"EXT",		);

class MO(_reg.Reg):	pass
MO(0x00000001,	"READ",		);
MO(0x00000002,	"WRITE",	);
MO(0x00000004,	"APPEND",	);
MO(0x00000008,	"CREAT",	);
MO(0x00000010,	"TRUNC",	);
MO(0x00000020,	"EXCL",		);

## statvfs@openssh.com f_flag flags */
class EXT(_reg.Reg):	pass
EXT(0x00000001,	"Xstatvfs_RDONLY",	);
EXT(0x00000002,	"Xstatvfs_NOSUID",	);

class RET(_reg.Reg):	pass
RET(0, "OK",			'Success',			);
RET(1, "EOF",			'End of file',			);
RET(2, "NO_SUCH_FILE",		'No such file',			);
RET(3, "PERMISSION_DENIED",	'Permission denied',		);
RET(4, "FAILURE",		'Failure',			);
RET(5, "BAD_MESSAGE",		'Bad message',			);
RET(6, "NO_CONNECTION",		'No connection',		);
RET(7, "CONNECTION_LOST",	'Connection lost',		);
RET(8, "OP_UNSUPPORTED",	'Operation unsupported',	);

