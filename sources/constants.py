#constants for sources

from enum import IntFlag, auto

class sourceStatus(IntFlag):
	RUNNING = auto()
	DONE = auto()
