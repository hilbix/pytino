# Allow calls of sync to async and vice versa (Python 3.6 and above)
#
# NOT READY YET
#
# vim:set ts=8:
#
# This Works is placed under the terms of the Copyright Less License,
# see file COPYRIGHT.CLL.  USE AT OWN RISK, ABSOLUTELY NO WARRANTY.
#
# BTW WTF why are essential batteries missing in Python nowadays?

import	asyncio

# WTF!?!
# asyncio.Task.current_task isn't portable because it will vanish
# asyncio.current_task isn't portable because it is not in Python 3.6
# https://docs.python.org/3/library/asyncio-task.html#asyncio.Task.current_task WTF
#
# So use pytino.async.current_task instead.
# I consider such needed hacks from being far beyond any bearable level of insanity:
try:
	current_task	= asyncio.current_task
except:
	current_task	= asyncio.Task.current_task

