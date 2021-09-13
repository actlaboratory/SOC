from enum import Enum,auto

class job(Enum):
	CREATED = auto()
	STARTED = auto()
	ADDED_ITEM = auto()
	CONVERTED_ITEM = auto()
	PROCESSED = auto()
	CANCELED = auto()

class engine(Enum):
	STARTED = auto()
	STOPED = auto()

class source(Enum):
	END = auto()
	