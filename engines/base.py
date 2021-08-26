#engine base

import queue
import time
import threading
import constants
from logging import getLogger
import errorCodes
import converter
from .constants import engineStatus

class engineBase(threading.Thread):
	"""すべてのエンジンクラスが継承する基本クラス。"""

	messageQueue = queue.Queue()

	def __init__(self, identifier):
		self.identifier = identifier
		self.log = getLogger("%s.%s" % (constants.APP_NAME, self.identifier))
		self.log.info("initialized")
		super().__init__()
		self.status = 0
		self._jobQueue = queue.Queue()
		self._onAfterRecognize = lambda a: None
		self.raiseStatusFlag(engineStatus.RUNNING)

	def put(self, job):
		self.log.debug("job received")
		self.raiseStatusFlag(engineStatus.CONVERTER_PROCESSING)
		converter.convert(job, self.getSupportedFormats())
		self.lowerStatusFlag(engineStatus.CONVERTER_PROCESSING)
		self._jobQueue.put(job)

	def setCallbackOnAfterRecognize(self, callback):
		self._onAfterRecognize = callback

	def run(self):
		self.log.debug("thread started")
		while True:
			time.sleep(0.01)
			if self._jobQueue.empty():
				if self.getStatus() & engineStatus.SOURCESTOPED:
					break
				continue
			job = self._jobQueue.get()
			self.log.debug("executing recognition...")
			self.raiseStatusFlag(engineStatus.EXECUTING)
			self._execRecognize(job)
			self.log.debug("finished recognition")
			self._onAfterRecognize(job)
			self.lowerStatusFlag(engineStatus.EXECUTING)
		self.log.debug("finish engine thread")
		self.lowerStatusFlag(engineStatus.RUNNING)
		self.raiseStatusFlag(engineStatus.FINISHED)

	def _recognize(self, item):
		raise NotImplementedError()

	def _execRecognize(self, job):
		for item in job.items:
			self._recognize(item)

	def notifyStopSource(self):
		self.log.debug("notifyed source stoped")
		self.raiseStatusFlag(engineStatus.SOURCESTOPED)

	def getSupportedFormats(self):
		return 0

	def raiseStatusFlag(self, flag):
		assert isinstance(flag, engineStatus)
		self.status |= flag

	def lowerStatusFlag(self, flag):
		assert isinstance(flag, engineStatus)
		self.status &= -1-flag

	def getStatus(self):
		return self.status


	def _showMessage(self, text):
		result = queue.Queue()
		data = (text, result)
		self.messageQueue.put(data)
		while not result.empty():
			time.sleep(0.01)
		return result.get()
