from enum import enum,auto

class job(enum):
	CREATED = auto()
	STARTED = auto()
	ADDED_ITEM = auto()
	CONVERTED_ITEM = auto()
	PROCESSED = auto()
	CANCELED = auto()

class engine(enum):
	STARTED = auto()
	STOPED = auto()

class source(enum):
	END = auto()
	