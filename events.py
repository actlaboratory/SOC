from enum import enum,auto


class job(enum):
	CREATED = auto()
	CONVERTQUEUE_EMPTY = auto()
	PROCESSQUEUE_EMPTY = auto()
	NAME_CHANGED = auto()
	SOURCE_END = auto()
	CONVERT_COMPLETED = auto()
	PROCESS_COMPLETED = auto()
	CANCELED = auto()

class engine(enum):
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
