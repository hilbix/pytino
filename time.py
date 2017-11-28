# Standard time tools

from __future__ import absolute_import

import time

def UTCstamp():
	t	= time.gmtime()
	return "%04d%02d%02d-%02d%02d%02d" % ( t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)

