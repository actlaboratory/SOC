#engine base

import queue
import time
import threading
import constants
from logging import getLogger, setLogRecordFactory
import errorCodes
import converter
from .constants import engineStatus
import events
import jobObjects
from jobObjects import jobStatus

class engineBase(threading.Thread):
	"""すべてのエンジンクラスが継承する基本クラス。"""
	_name = None

	def __init__(self, identifier):
		self.identifier = identifier
		self.log = getLogger("%s.%s" % (constants.APP_NAME, self.identifier))
		super().__init__()
		self.log.info("created")
		self.status = engineStatus(0)
		self.onEvent = None
		self.jobQueue = queue.Queue()

	def getName(self):
		name = self._name
		if name is None:
			raise NotImplementedError
		return name

	def setOnEvent(self, callBack):
		assert callable(callBack)
		self.onEvent = callBack

	def initable(self):
		return True

	def initialize(self, *args, **kwargs):
		self._init(*args, **kwargs)
		self.onEvent(events.engine.INITIALIZED, engine = self)
		self.log.info("initialized")

	def _init(self):
		return

	def run(self):
		self.onEvent(events.engine.STARTED, engine = self)
		self.raiseStatusFlag(engineStatus.RUNNING)
		self._run()
		self.log.debug("thread finished")
		self.lowerStatusFlag(engineStatus.RUNNING)
		self.raiseStatusFlag(engineStatus.DONE)
		self.onEvent(events.engine.STOPED, engine = self)

	def _run(self):
		while True:
			time.sleep(0.01)
			if self.jobQueue.empty():
				if self.getStatus() & engineStatus.SOURCE_END:
					break
				continue
			job = self.jobQueue.get()
			self._processJob(job)

	def _processJob(self, job:jobObjects.job):
		while not job.getStatus() & jobStatus.PROCESS_COMPLETE:
			time.sleep(0.01)
			item = job.getProcessItem()
			if not item:
				continue
			self._recognize(item)
			job.addProcessedItem(item)

	def _recognize(self, item):
		raise NotImplementedError()

	def endSource(self):
		self.raiseStatusFlag(engineStatus.SOURCE_END)

	def getSupportedFormats(self):
		return 0

	def addJob(self, job):
		self.jobQueue.put(job)

	def raiseStatusFlag(self, flag):
		assert isinstance(flag, engineStatus)
		self.status |= flag

	def lowerStatusFlag(self, flag):
		assert isinstance(flag, engineStatus)
		self.status &= -1-flag

	def getStatus(self):
		return self.status
