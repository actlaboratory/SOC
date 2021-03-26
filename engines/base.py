#engine base

import queue
import time
import threading
import constants
from logging import getLogger
import errorCodes
import converter

class engineBase(threading.Thread):
	"""すべてのエンジンクラスが継承する基本クラス。"""

	messageQueue = queue.Queue()

	def __init__(self, identifier):
		self.identifier = identifier
		self.log = getLogger("%s.%s" % (constants.APP_NAME, self.identifier))
		self.log.info("initialized")
		super().__init__()
		self._status = errorCodes.OK
		self._itemQueue = queue.Queue()
		self._onAfterRecognize = None

	def put(self, item):
		self.log.debug("item received")
		converter.convert(item,self.getSupportedFormats())
		self._itemQueue.put(item)

	def setCallbackOnAfterRecognize(self, callback):
		self._onAfterRecognize = callback

	def run(self):
		self.log.debug("thread started")
		while True:
			time.sleep(0.01)
			if self._itemQueue.empty():
				if self._status & errorCodes.STATUS_ENGINE_STOPSOURCE == errorCodes.STATUS_ENGINE_STOPSOURCE:break
				continue
			if self._status & errorCodes.STATUS_ENGINE_NEEDSTOP == errorCodes.STATUS_ENGINE_NEEDSTOP:
				break
			item = self._itemQueue.get()
			self.log.debug("executing recognition...")
			self._recognize(item)
			self.log.debug("finished recognition")
			self._onAfterRecognize(item)
		self.log.debug("finish engine thread")
		self._status |= errorCodes.STATUS_ENGINE_FINISHED

	def _recognize(self, item):
		raise NotImplementedError()

	def notifyStopSource(self):
		self.log.debug("notifyed source stoped")
		self._status |= errorCodes.STATUS_ENGINE_STOPSOURCE

	def getSupportedFormats(self):
		return 0

	def getEngineStatus(self):
		return self._status

	def _showMessage(self, text):
		result = queue.Queue()
		data = (text, result)
		self.messageQueue.put(data)
		while not result.empty():
			time.sleep(0.01)
		return result.get()

	def getStatusString(self):
		return _("未定義")


	def interrupt(self):
		self._status |= errorCodes.STATUS_ENGINE_INTERRUPT

