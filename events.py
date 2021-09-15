from enum import Enum,auto
import enum

class job(Enum):
	CREATED = auto()
	CONVERTQUEUE_EMPTY = auto()
	PROCESSQUEUE_EMPTY = auto()
	NAME_CHANGED = auto()
	SOURCE_END = auto()
	CONVERT_COMPLETED = auto()
	PROCESS_COMPLETED = auto()
	CANCELED = auto()

class engine(Enum):
	INITIALIZED = auto()
	STARTED = auto()
	STOPED = auto()

class source(enum):
	INITIALIZED = auto()
	STARTED = auto()
	END = auto()
	TERMINATED = auto()

class item(enum):
	ADDED = auto()
	CONVERT_STARTED = auto()
	CONVERTED = auto()
	PROCESS_STARTED = auto()
	PROCESSED = auto()

class converter(enum):
	STARTED = auto()
	STOPED = auto()
