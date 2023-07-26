#sourceBase

import threading

import askEvent
import constants
import events

from logging import getLogger

from sources.constants import sourceStatus


class sourceBase(threading.Thread):
	def __init__(self, identifier):
		self.identifier = identifier# このソースを表す文字列
		self.log=getLogger("%s.%s" % (constants.LOG_PREFIX,identifier))
		self.log.debug("created")
		self.status = sourceStatus(0)
		super().__init__()
		self.onEvent = None
		self.onAskEvent = None
		self.engine = None

	def setOnAskEvent(self, callback):
		assert callable(callback)
		self.onAskEvent = callback

	def _init(self):
		return

	def setOnEvent(self, callback):
		assert callable(callback)
		self.onEvent = callback

	def initialize(self, engine):
		self.engine=engine
		self._init()
		self.onEvent(events.source.INITIALIZED, source = self)
		self.log.debug("initialized")

	def run(self):
		self.log.info("started")
		self.onEvent(events.source.STARTED, source = self)
		self.raiseStatusFlag(sourceStatus.RUNNING)
		self._run()
		self.lowerStatusFlag(sourceStatus.RUNNING)
		self.log.info("end")
		self.terminate()
		self.onEvent(events.source.END)
		self.raiseStatusFlag(sourceStatus.DONE)

	def _run(self):
		return

	def onJobCreated(self, job):
		self.onEvent(events.job.CREATED, job = job, source = self)

	def terminate(self):
		"""ソースを閉じるときの処理"""
		self._final()


	def _final(self):
		return

	def ask(self, event):
		self.onAskEvent(event)
		return event.getResult()

	def raiseStatusFlag(self, flag):
		assert isinstance(flag, sourceStatus)
		self.status |= flag

	def lowerStatusFlag(self, flag):
		assert isinstance(flag, sourceStatus)
		self.status &= -1-flag

	def getStatus(self):
		return self.status

class sourceAskEvent(askEvent.askEventBase):
	pass
