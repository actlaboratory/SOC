from enum import IntFlag, auto

class engineStatus(IntFlag):
	SOURCE_END = auto()
	RUNNING = auto()
	DONE = auto()
