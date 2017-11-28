# Python introspection to some standard libraries and more
# Warning, this is somewhat slow at init time, but later very fast

from __future__ import absolute_import

import pytino

def _impl(_get):
	# Nuke a secondary invocation, the first invocation wins
	pytino.introspection._impl = lambda x: None

	_mod = None

	def set(name, prefix, what):
		pytino.introspection.__setattr__(name, _get(_mod, prefix, _mod+what))

	_mod = 'select'

	set('selEPOLL',    'EPOLL',    '.epoll')
	set('selPOLL',     'POLL',     '.poll')
	
	_mod = 'os'
	
	set('osEX',        'EX_',      ' exception')
	set('osO',         'O_',       ' open')
	set('osP',         'P_',       ' proc')
	set('osSEEK',      'SEEK_',    ' seek')
	set('osST',        'ST_',      ' stat')
	set('osW',         'W',        ' wait')
	
	_mod = 'socket'
	
	set('sockAF',      'AF_',      ' family')
	set('sockSOCK',    'SOCK_',    ' type')
	set('sockIPPROTO', 'IPPROTO_', ' proto')
	set('sockIPV6',    'IPV6_',    ' ipv6')
	set('sockIP',      'IP_',      ' ip')
	set('sockMSG',     'MSG_',     ' msg')
	set('sockTCP',     'TCP_',     ' TCP')
	
	set('sockAI',      'AI_',      ' AI')
	set('sockEAI',     'EAI_',     ' EAI')
	set('sockTIPC',    'TIPC_',    ' TIPC')
	set('sockHCI',     'HCI_',     ' HCI')
	set('sockINADDR',  'INADDR_',  ' INADDR')
	set('sockIPPORT',  'IPPORT_',  ' IPPORT')
	set('sockBTPROTO', 'BTPROTO_', ' BTPROTO')
	set('sockBDADDR',  'BDADDR_',  ' BDADDR')
	set('sockNETLINK', 'NETLINK_', ' NETLINK')
	set('sockNI',      'NI_',      ' NI')
	set('sockPACKET',  'PACKET_',  ' PACKET')
	set('sockSOL',     'SOL_',     ' SOL')
	set('sockSHUT',    'SHUT_',    ' SHUT')
	set('sockRAND',    'RAND_',    ' RAND')
	set('sockSO',      'SO_',      ' SO')
	set('sockSSL',     'SSL_',     ' SSL')
