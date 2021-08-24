#constants for sources

from enum import Flag, auto

class sourceStatus(Flag):
	QUEUED = auto()
	RUNNING = auto()
	