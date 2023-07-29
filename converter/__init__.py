import queue
import threading
import time
import wx

import askEvent
import constants
import events
import jobObjects

from logging import getLogger

from .converterStatus import converterStatus
from .pdf2image import pdf2image
from . import pillow


converter_list = [pillow.pillow, pdf2image]

class converter(threading.Thread):
	def __init__(self, engineSupportedFormats):
		self.engineSupportedFormats = engineSupportedFormats
		super().__init__()
		self.log = getLogger("%s.convertor" % constants.LOG_PREFIX)
		self.jobQueue = queue.Queue()
		self.onAskEvent = None
		self.onEvent = None
		self.status = converterStatus(0)

	def ask(self, event):
		self.onAskEvent(event)
		if event.getSelectionCount() <= 1:
			return wx.ID_OK
		return event.getResult()

	def setOnAskEvent(self, callback):
		assert callable(callback)
		self.onAskEvent = callback

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
				pillow.convertGrayScale(converted_item)
				job.addConvertedItem(converted_item)
			elif type(converted_item) == list:
				for itm in converted_item:
					pillow.convertGrayScale(itm)
					job.addConvertedItem(itm)
		job.endConvert()

	def _convertItem(self, item):
		if item.getFormat() & self.engineSupportedFormats:
			# 返還不要
			self.log.info("convert is not needed")
			return item
		for converter in converter_list:
			if not (converter.getSupportedFormats() & item.getFormat()):
				# コンバータが未対応なので別のを試す
				continue

			# 変換先形式を決める
			for format in constants.IMAGE_FORMAT_LIST:
				if (converter.getConvertableFormats() & format) & (self.engineSupportedFormats & format):
					c = converter(item)
					self.log.info("use:"+str(converter))
					return c.convert(format)
		# 変換できない
		self.log.error("cannot convert:" + str(item.getFormat()) + " to " + str(self.engineSupportedFormats))
		self.ask(askEvent.notice(_("ファイル形式エラー"), _("指定されたファイルとエンジンの形式の組み合わせが不正です。\nファイルの形式に対応したエンジンを指定してください。")))

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
