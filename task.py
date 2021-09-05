from enum import IntFlag, auto
import threading
from logging import getLogger
import constants
from sources.constants import sourceStatus
from engines.constants import engineStatus
import time
import winsound

class task(threading.Thread):
	def __init__(self, source, engine):
		super().__init__()
		self.source = source
		self.engine = engine
		self.jobs = []
		self.log = getLogger("%s.task" % (constants.APP_NAME))
		self.log.debug("initialized")

	def run(self):
		self.raiseStatusFlag(taskStatus.STARTED)
		self.log.debug("initializing modules...")
		self.source.initialize()
		self.source.start()
		self.engine.setCallbackOnAfterRecognize(self.onAfterRecognize)
		self.engine.start()
		self.log.info("Ocr started")
		time.sleep(1)
		while True:
			if not self.source.getStatus() & sourceStatus.RUNNING:
				if self.source.empty():
					break
			if self.source.empty():
				time.sleep(0.1)
				continue
			job = self.source.getNextJob()
			self.jobs.append(job)
			self.log.debug("job received")
			self.engine.put(job)
			time.sleep(0.01)
		self.engine.notifyStopSource()
		while not self.engine.getStatus() & engineStatus.FINISHED:
			time.sleep(0.01)
		self.log.debug("Ocr done!")
		self.raiseStatusFlag(taskStatus.DONE)

	def getJobs(self):
		return self.jobs

	def getProcessedJobs(self):
		return self.jobs

	def getAllText(self):
		text = ""
		for job in self.getProcessedJobs():
			text += job.getAllItemText()
		return text

	def getEngineStatus(self):
		return self.engine.getStatus()

	def getSourceStatus(self):
		return self.source.getStatus()

	def onAfterRecognize(self, job):
		self.log.info("processed job received")
		winsound.Beep(1000, 200)

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

