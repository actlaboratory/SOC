from enum import Flag, auto

class engineStatus(Flag):
	RUNNING = auto()
	CONVERTER_PROCESSING = auto()
	FINISHED = auto()
	EXECUTING = auto()
	SOURCESTOPED = auto()
	