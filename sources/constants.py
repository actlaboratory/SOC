#constants for sources

from enum import IntFlag, auto

class sourceStatus(IntFlag):
	QUEUED = auto()
	RUNNING = auto()
