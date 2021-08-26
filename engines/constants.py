from enum import IntFlag, auto

class engineStatus(IntFlag):
	RUNNING = auto()
	CONVERTER_PROCESSING = auto()
	FINISHED = auto()
	EXECUTING = auto()
	SOURCESTOPED = auto()
	