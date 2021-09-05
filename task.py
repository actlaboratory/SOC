from enum import IntFlag, auto

class task:
	def __init__(self, source, engine):
		self.source = source
		self.engine = engine
		self.jobs = []

	def getJobs(self):
		return self.jobs

	def getEngineStatus(self):
		return self.engine.getStatus()

	def getSourceStatus(self):
		return self.source.getStatus()

class taskStatus(IntFlag):
	STARTED = auto()
	DONE = auto()

