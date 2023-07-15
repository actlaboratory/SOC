from enum import Enum,auto

class job(Enum):
	CREATED = auto()
	CONVERTQUEUE_EMPTY = auto()
	PROCESSQUEUE_EMPTY = auto()
	NAME_CHANGED = auto()
	SOURCE_END = auto()
	CONVERT_STARTED = auto()
	CONVERT_COMPLETED = auto()
	PROCESS_STARTED = auto()
	PROCESS_COMPLETED = auto()
	CANCELED = auto()
	STATUS_CHANGED = auto()

class engine(Enum):
	INITIALIZED = auto()
	STARTED = auto()
	JOBPROCESS_STARTED = auto()
	JOBPROCESS_COMPLETE = auto()
	STOPED = auto()

class source(Enum):
	INITIALIZED = auto()
	STARTED = auto()
	END = auto()
	TERMINATED = auto()

class item(Enum):
	ADDED = auto()
	CONVERT_STARTED = auto()
	CONVERTED = auto()
	PROCESS_STARTED = auto()
	PROCESSED = auto()

class converter(Enum):
	STARTED = auto()
	STOPED = auto()
