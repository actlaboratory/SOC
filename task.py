class task:
	def __init__(self, source, engine):
		self._source = source
		self._engine = engine
		self.jobs = []

	@property
	def source(self):
		return _source

	@property
	def engine(self):
		return self._engine

	def getJobs(self):
		return self.jobs
