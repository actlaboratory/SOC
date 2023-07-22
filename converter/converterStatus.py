from enum import IntFlag,auto

class converterStatus(IntFlag):
	RUNNING = auto()
	JOB_END = auto()
	DONE = auto()
