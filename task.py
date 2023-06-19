from enum import IntFlag, auto
import threading
from logging import getLogger
import constants
from sources.constants import sourceStatus
from engines.constants import engineStatus
import time
import winsound
import events
import converter
import jobObjects

nextTask_id = 1

class task(threading.Thread):
	def __init__(self, source, engine):
		global nextTask_id
		super().__init__()
		self.source = source
		self.engine = engine
		self.source.setOnEvent(self.onEvent)
		self.source.setOnAskEvent(self.onAskEvent)
		self.engine.setOnEvent(self.onEvent)
		self.engine.setOnAskEvent(self.onAskEvent)
		self.converter = converter.converter(engine.getSupportedFormats())
		self.converter.setOnEvent(self.onEvent)
		self.higherOnEvent = None
		self.higherOnAskEvent = None
		self.jobs = []
		self.id = nextTask_id
		nextTask_id += 1
		self.log = getLogger("%s.task-%d" % (constants.APP_NAME, self.id))
		self.log.info("initialized")
		self.status = taskStatus(0)

	def setOnEvent(self, callback):
		assert callable(callback)
		self.higherOnEvent = callback


	def setOnAskEvent(self, callback):
		assert callable(callback)
		self.higherOnAskEvent = callback

	def onEvent(self, event, job = None, item = None, source = None, engine = None, converter = None):
		self.log.debug("called onEvent with %s" % (str(event)))
		if event == events.job.CREATED:
			self.registJob(job)
		elif event == events.source.END:
			self.converter.endJob()
			self.engine.endSource()
			self.log.info("Notified the end of the source")
		self.higherOnEvent(event, engine = engine, source = source, job = job, item = item, converter = converter, task = self)

	def onAskEvent(self, askEvent):
		self.higherOnAskEvent(askEvent, self)

	def startSource(self):
		self.source.initialize()
		self.log.debug("source initialized")
		self.source.start()

	def registJob(self, job:jobObjects.job):
		job.setOnEvent(self.onEvent)
		self.jobs.append(job)
		self.converter.addJob(job)
		self.engine.addJob(job)
		self.log.debug("registered job-%d" % job.getID())

	def startEngine(self):
		self.engine.initialize()
		self.log.debug("engine initialized")
		self.engine.start()

	def startConverter(self):
		self.converter.start()
		self.log.debug("converter started")

	def getJobs(self):
		return self.jobs

	def getEngine(self):
		return self.engine

	def getEngineStatus(self):
		return self.engine.getStatus()

	def getSourceStatus(self):
		return self.source.getStatus()

	def getID(self):
		return self.id

	def raiseStatusFlag(self, flag):
		assert isinstance(flag, taskStatus)
		self.status |= flag

	def lowerStatusFlag(self, flag):
		assert isinstance(flag, taskStatus)
		self.status &= -1-flag

	def getStatus(self):
		return self.status


class taskStatus(IntFlag):
	STARTED = auto()
	DONE = auto()
