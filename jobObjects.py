from os.path import basename
import errorCodes
import constants
import os
import re
import subprocess
import namedPipe
import globalVars
import datetime
import util
from enum import IntFlag, auto
import queue
import events
from logging import getLogger

next_job_id = 1

class job():
	def __init__(self, path = None, temp = True):
		global next_job_id
		self._path = path
		self._id = next_job_id
		next_job_id += 1
		self._temp = temp
		if path:
			self._name = os.path.basename(path)
		else:
			self._name = "job-%d" % self.id
		self.onEvent = None
		self.log = getLogger("%s.job-%s" % (constants.APP_NAME, self.getID()))
		self.log.info("created job named %s" % (self.getName()))
		self.convertQueue = queue.Queue()
		self.processQueue = queue.Queue()
		self.processedItem = []
		self.status = jobStatus(0)

	def setOnEvent(self, callback):
		assert callable(callback)
		self.onEvent = callback

	def getName(self):
		return self._name

	def setName(self, name):
		self._name = name
		self.onEvent(events.job.NAME_CHANGED, job = self)

	def addCreatedItem(self, item):
		self.convertQueue.put(item)
		self.onEvent(events.item.ADDED, job = self, item = item)

	def getConvertItem(self):
		if self.convertQueue.empty():
			self.onEvent(events.job.CONVERTQUEUE_EMPTY, job = self)
			return None
		item = self.convertQueue.get()
		self.onEvent(events.item.CONVERT_STARTED, job = self, item = item)
		return item

	def addConvertedItem(self, item):
		self.processQueue.put(item)
		self.onEvent(events.item.CONVERTED, job = self, item = item)
		if self.convertQueue.empty() & (self.getStatus() & jobStatus.SOURCE_END):
			self.raiseStatusFlag(jobStatus.CONVERT_COMPLETE)
			self.log.info("convert completed")
			self.onEvent(events.job.CONVERT_COMPLETED, job = self)

	def getProcessItem(self):
		if self.processQueue.empty():
			self.onEvent(events.job.PROCESSQUEUE_EMPTY, job = self)
			return None
		item = self.processQueue.get()
		self.onEvent(events.item.PROCESS_STARTED, job = self, item = item)
		return item

	def addProcessedItem(self, item):
		self.processedItem.append(item)
		self.onEvent(events.item.PROCESSED, job = self, item = item)
		self.log.debug("item processed")
		if self.processQueue.empty() & bool(self.getStatus() & jobStatus.CONVERT_COMPLETE):
			self.raiseStatusFlag(jobStatus.PROCESS_COMPLETE)
			self.log.debug("process completed")
			self.onEvent(events.job.PROCESS_COMPLETED, job = self)

	def endSource(self):
		self.raiseStatusFlag(jobStatus.SOURCE_END)
		self.onEvent(events.job.SOURCE_END, job = self)

	def getAllItemText(self):
		text = ""
		for item in self.processedItem:
			text += item.getText()
		return text

	def getProcessedItems(self):
		return self.processedItem

	def raiseStatusFlag(self, flag):
		assert isinstance(flag, jobStatus)
		self.status |= flag

	def lowerStatusFlag(self, flag):
		assert isinstance(flag, jobStatus)
		self.status &= -1-flag

	def getStatus(self):
		return self.status

	def getID(self):
		return self._id

class item:
	def __init__(self, path):
		self.path = path
		self.done = False

	def getPath(self):
		return self.path

	def getFormat(self):
		if not hasattr(self, "format"):
			self._register_format()
		return self.format

	def _register_format(self):
		ext = os.path.splitext(self.getPath())[1][1:]
		format = constants.EXT_TO_FORMAT.get(ext.lower(), constants.FORMAT_UNKNOWN)
		if format == constants.FORMAT_PDF_UNKNOWN:
			# 埋め込みテキストの含まれるPDFであるか判定
			pipeServer = namedPipe.Server(constants.PIPE_NAME)
			pipeServer.start()
			subprocess.run(("pdftotext", self.getPath(), pipeServer.getFullName()))
			list = pipeServer.getNewMessageList()
			pipeServer.exit()
			text = list[0]
			if re.search(r'[^\f\n\r]', text) == None:
				format = constants.FORMAT_PDF_TEXT
			else:
				format = constants.FORMAT_PDF_IMAGE
		self.format = format

	def setText(self, text):
		self.text = text
		self.done = True

	def getText(self):
		return self.text

	def isDone(self):
		return self.done

class jobStatus(IntFlag):
	SOURCE_END = auto()
	CONVERT_COMPLETE = auto()
	PROCESS_COMPLETE = auto()
