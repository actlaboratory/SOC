import errorCodes
import threading
import time
import queue
from logging import getLogger
import constants
from sources.constants import sourceStatus
from engines.constants import engineStatus

class manager(threading.Thread):
	def __init__(self, engine, source):
		super().__init__()
		self.processedJob = []
		self.engine = engine
		self.source = source
		self.running = True
		self._messageQueue = queue.Queue()
		self.log = getLogger("%s.manager" % (constants.APP_NAME))

	def run(self):
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
			item = self.source.get_item()
			self.log.debug("item received")
			self.engine.put(item)
			time.sleep(0.01)
		self.engine.notifyStopSource()
		while not self.engine.getStatus() & engineStatus.FINISHED:
			time.sleep(0.01)
		self.log.debug("Ocr stoped")
		self.running = False
		return

	def onAfterRecognize(self, job):
		self.processedJob.append(job)

	def getEngineStatus(self):
		return self.engine.getStatus()

	def getSourceStatus(self):
		return self.source.getStatus()

	def getProcessedJobs(self):
		return self.processedJob

	def getAllText(self):
		text = ""
		for job in self.getProcessedJobs():
			text += job.getAllItemText()
		return text
