import errorCodes
import threading
import time
import queue
from logging import getLogger
import constants

class manager(threading.Thread):
	def __init__(self, engine, source):
		super().__init__()
		self.processedJob = []
		self.engine = engine
		self.source = source
		self.done = False
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
			if self.source.getStatus() & errorCodes.STATUS_SOURCE_EMPTY == errorCodes.STATUS_SOURCE_EMPTY and self.source.getStatus() & errorCodes.STATUS_SOURCE_QUEUED != errorCodes.STATUS_SOURCE_QUEUED:
				break
			if self.source.getStatus() & errorCodes.STATUS_SOURCE_LOADING == errorCodes.STATUS_SOURCE_LOADING and self.source.getStatus() & errorCodes.STATUS_SOURCE_QUEUED != errorCodes.STATUS_SOURCE_QUEUED:
				time.sleep(0.1)
				continue
			item = self.source.get_item()
			self.log.debug("item received")
			self.engine.put(item)
			time.sleep(0.01)
		self.engine.notifyStopSource()
		while not self.engine.getEngineStatus() & errorCodes.STATUS_ENGINE_FINISHED == errorCodes.STATUS_ENGINE_FINISHED:
			time.sleep(0.01)
		self.log.debug("Ocr stoped")
		self.done = True
		return

	def onAfterRecognize(self, job):
		self.processedJob.append(job)

	def getStatusString(self):
		statuses = {}
		statuses["source"] = self.source.getStatusString()
		statuses["engine"] = self.engine.getStatusString()
		return statuses

	def getText(self):
		text = ""
		for job in self.processedJob:
			for item in job.items:
				if item.success:
					text += item.getText()
		return text

	def updateMessageQueue(self):
		while not self.source.messageQueue.empty():
			self._messageQueue.put(self.source.messageQueue.get())
		while not self.engine.messageQueue.empty():
			self._messageQueue.put(self.engine.messageQueue.get())

	def getMessage(self):
		if self.isMessageEmpty():
			return
		return self._messageQueue.get()

	def isMessageEmpty(self):
		return self._messageQueue.empty()

	def isDone(self):
		return self.done
