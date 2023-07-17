import time
import queue
from logging import exception, getLogger
import constants
from sources.constants import sourceStatus
from engines.constants import engineStatus
from task import taskStatus
import events
import wx

class manager():
	def __init__(self):
		super().__init__()
		self.tasks = []
		self.log = getLogger("%s.manager" % (constants.APP_NAME))
		self.log.info("initialized")
		self.runningSourceIndex = -1
		self.runningEngineIndex = -1
		self.runningConverterIndex = -1
		self.higherOnEvent = None
		self.higherOnAskEvent = None

	def setOnEvent(self, callBack):
		assert callable(callBack)
		self.higherOnEvent = callBack

	def onEvent(self, event, task, job = None, item = None, source = None, engine = None, converter = None):
		self.log.debug("called onEvent with %s" % (event))
		if event == events.source.END:
			if self.runningSourceIndex < len(self.tasks) -1:
				self.tasks[self.runningSourceIndex+1].startSource()
				self.runningSourceIndex += 1
			elif self.runningSourceIndex == len(self.tasks) -1:
				self.runningSourceIndex = -1
			else:
				raise exception("タスクの管理でエラーが発生しました。", self.runningSourceIndex)
		elif event == events.engine.STOPED:
			if self.runningEngineIndex < len(self.tasks) -1:
				self.tasks[self.runningEngineIndex+1].startEngine()
				self.runningEngineIndex += 1
			elif self.runningEngineIndex == len(self.tasks) -1:
				self.runningEngineIndex = -1
			else:
				raise exception("タスクの管理でエラーが発生しました。", self.runningSourceIndex)
		elif event == events.converter.STOPED:
			if self.runningConverterIndex < len(self.tasks) -1:
				self.tasks[self.runningConverterIndex+1].startEngine()
				self.runningConverterIndex += 1
			elif self.runningConverterIndex == len(self.tasks) -1:
				self.runningConverterIndex = -1
			else:
				raise exception("タスクの管理でエラーが発生しました。", self.runningSourceIndex)
		wx.CallAfter(self.higherOnEvent,event,job = job, item = item, engine = engine, source = source, converter = converter)

	def setOnAskEvent(self, callback):
		assert callable(callback)
		self.higherOnAskEvent = callback

	def onAskEvent(self, askEvent, task):
		wx.CallAfter(self.higherOnAskEvent, askEvent, task)

	def addTask(self, task):
		self.log.debug("added task-%d" % task.getID())
		task.setOnEvent(self.onEvent)
		task.setOnAskEvent(self.onAskEvent)
		self.tasks.append(task)
		if self.runningSourceIndex == -1:
			task.startSource()
			self.runningSourceIndex = len(self.tasks) - 1
		if self.runningEngineIndex == -1:
			task.startEngine()
			self.runningEngineIndex = len(self.tasks) - 1
		if self.runningConverterIndex == -1:
			task.startConverter()
			self.runningConverterIndex = len(self.tasks) - 1

	def getTasks(self):
		return self.tasks

