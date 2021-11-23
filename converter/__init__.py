import queue
from . import pillow
from .pdf2image import pdf2image
import jobObjects
from jobObjects import jobStatus
import threading
from .constants import converterStatus
import constants
import globalVars
import events
import time

converter_list = [pillow.pillow, pdf2image]

class converter(threading.Thread):
	def __init__(self, engineSupportedFormats):
		self.engineSupportedFormats = engineSupportedFormats
		super().__init__()
		self.jobQueue = queue.Queue()
		self.onEvent = None
		self.status = converterStatus(0)

	def setOnEvent(self, callback):
		assert callable(callback)
		self.onEvent = callback

	def run(self):
		self.raiseStatusFlag(converterStatus.RUNNING)
		self.onEvent(events.converter.STARTED, converter = self)
		while True:
			time.sleep(0.01)
			if self.jobQueue.empty():
				if self.getStatus() & converterStatus.JOB_END:
					break
				continue
			job = self.jobQueue.get()
			self._convertJob(job)
		self.lowerStatusFlag(converterStatus.RUNNING)
		self.raiseStatusFlag(converterStatus.DONE)
		self.onEvent(events.converter.STOPED, converter = self)

	def _convertJob(self, job: jobObjects.job):
		while True:
			time.sleep(0.01)
			item = job.getConvertItem()
			if item == None:
				break
			converted_item = self._convertItem(item)
			if type(converted_item) == jobObjects.item:
				job.addConvertedItem(converted_item)
			elif type(converted_item) == list:
				for itm in converted_item:
					job.addConvertedItem(itm)
		job.endConvert()

	def _convertItem(self, item):
		if item.getFormat() & self.engineSupportedFormats:
			return item
		for converter in converter_list:
			if not (converter.getSupportedFormats() & item.getFormat()):
				continue
			for format in constants.IMAGE_FORMAT_LIST:
				if (converter.getConvertableFormats() & format) & (self.engineSupportedFormats & format):
					c = converter(item)
					return c.convert(format)

	def addJob(self, job):
		self.jobQueue.put(job)

	def endJob(self):
		self.raiseStatusFlag(converterStatus.JOB_END)

	def raiseStatusFlag(self, flag):
		assert isinstance(flag, converterStatus)
		self.status |= flag

	def lowerStatusFlag(self, flag):
		assert isinstance(flag, converterStatus)
		self.status &= -1-flag

	def getStatus(self):
		return self.status

