#engine base

import queue
import threading
import time

import askEvent
import constants
import events
import jobObjects

from logging import getLogger

from .constants import engineStatus


class engineBase(threading.Thread):
	"""
		すべてのエンジンクラスが継承する基本クラス。
		初期化時の引数はなしとすること。本Baseクラスのコンストラクタの引数と異なるので注意
	"""


	def __init__(self, identifier):
		self.identifier = identifier
		self.log = getLogger("%s.%s" % (constants.APP_NAME, self.identifier))
		super().__init__()
		self.log.info("created")
		self.status = engineStatus(0)
		self.onEvent = None
		self.jobQueue = queue.Queue()
		self.onAskEvent = None

	@classmethod
	def getName(cls):
		"""
			ユーザーに見せる名前を返す
		"""
		raise NotImplementedError

	@classmethod
	def getSettingDialog(cls):
		"""
			ユーザーがエンジンの詳細設定を行うために利用できるDialogを返す
			ダイアログはviews.engines以下に格納すること。
		"""
		return None

	def setOnEvent(self, callBack):
		assert callable(callBack)
		self.onEvent = callBack

	def setOnAskEvent(self, callback):
		assert callable(callback)
		self.onAskEvent = callback

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
		self.onEvent(events.engine.JOBPROCESS_STARTED, engine = self, job = job)
		while True:
			time.sleep(0.01)
			item = job.getProcessItem()
			if item == None:
				break
			self._recognize(item)
			job.addProcessedItem(item)
		self.onEvent(events.engine.JOBPROCESS_COMPLETE, engine = self, job = job)
		job.endEngine()

	def _recognize(self, item):
		raise NotImplementedError()

	def endSource(self):
		self.raiseStatusFlag(engineStatus.SOURCE_END)

	def getSupportedFormats(self):
		return 0

	def addJob(self, job):
		self.jobQueue.put(job)

	def ask(self, askEvent):
		event = askEvent()
		self.onAskEvent(event)
		result = event.getResult()
		return result

	def raiseStatusFlag(self, flag):
		assert isinstance(flag, engineStatus)
		self.status |= flag

	def lowerStatusFlag(self, flag):
		assert isinstance(flag, engineStatus)
		self.status &= -1-flag

	def getStatus(self):
		return self.status

class engineAskEvent(askEvent.askEventBase):
	pass
