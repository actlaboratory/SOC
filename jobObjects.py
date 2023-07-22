

import namedPipe
import os
import queue
import re
import subprocess

import constants
import events
import globalVars

from enum import IntFlag, auto
from logging import getLogger

next_job_id = 1

class job():
	def __init__(self, path, temp, source, engine):
		global next_job_id
		self._path = path
		self._id = next_job_id
		next_job_id += 1
		self._temp = temp
		self._source = source
		self._engine = engine
		if path:
			self._name = os.path.basename(path)
		else:
			self._name = "file-%d" % self._id
		self.onEvent = None
		self.log = getLogger("%s.job-%s" % (constants.APP_NAME, self.getId()))
		self.log.info("created job named %s" % (self.getName()))
		self.convertQueue = queue.Queue()
		self.processQueue = queue.Queue()
		self.processedItem = [virtualAllPageItem(self)]
		self.status = jobStatus(0)
		self.totalCount = 0
		self.selectedPage = 0

	def setOnEvent(self, callback):
		assert callable(callback)
		self.onEvent = callback

	def getName(self):
		return self._name

	def getPath(self):
		return self._path

	def getSelectedPage(self):
		return self.selectedPage 

	def setName(self, name):
		self._name = name
		self.onEvent(events.job.NAME_CHANGED, job = self)

	def setSelectedPage(self, page):
		self.selectedPage = page

	def addCreatedItem(self, item):
		self.log.debug("item added")
		self.convertQueue.put(item)
		self.onEvent(events.item.ADDED, job = self, item = item)

	def getConvertItem(self):
		item = self.convertQueue.get(block=True)
		if not self.getStatus() & jobStatus.CONVERT_STARTED:
			self.onEvent(events.job.CONVERT_STARTED, job = self)
			self.raiseStatusFlag(jobStatus.CONVERT_STARTED)
		self.onEvent(events.item.CONVERT_STARTED, job = self, item = item)
		return item

	def addConvertedItem(self, item):
		self.processQueue.put(item)
		self.totalCount += 1
		self.onEvent(events.item.CONVERTED, job = self, item = item)
		globalVars.jobList[0].addConvertedItem(item)

	def getProcessItem(self):
		item = self.processQueue.get(block=True)
		if not self.getStatus() & jobStatus.PROCESS_STARTED:
			self.onEvent(events.job.PROCESS_STARTED, job = self)
			self.raiseStatusFlag(jobStatus.PROCESS_STARTED)
		self.onEvent(events.item.PROCESS_STARTED, job = self, item = item)
		return item

	def addProcessedItem(self, item):
		self.log.debug("item processed")
		item.setPageNumber(self.getProcessedCount() + 1)
		self.processedItem.append(item)
		globalVars.jobList[0].addProcessedItem(self,item)
		self.onEvent(events.item.PROCESSED, job = self, item = item)

	def endSource(self):
		self.convertQueue.put(None)
		self.raiseStatusFlag(jobStatus.SOURCE_END)
		self.onEvent(events.job.SOURCE_END, job = self)

	def endConvert(self):
		self.processQueue.put(None)
		self.raiseStatusFlag(jobStatus.CONVERT_COMPLETE)
		self.log.info("convert completed")
		self.onEvent(events.job.CONVERT_COMPLETED, job = self)

	def endEngine(self):
		self.raiseStatusFlag(jobStatus.PROCESS_COMPLETE)
		self.log.debug("process completed")
		self.onEvent(events.job.PROCESS_COMPLETED, job = self)

	def getAllItemText(self):
		return self.processedItem[0].getText()

	def getProcessedItems(self):
		return self.processedItem

	def getProcessedCount(self):
		return len(self.processedItem) -1

	def getTotalCount(self):
		return self.totalCount

	def raiseStatusFlag(self, flag):
		assert isinstance(flag, jobStatus)
		self.log.debug("raised %s" % (flag))
		self.status |= flag
		self.onEvent(events.job.STATUS_CHANGED, job = self)

	def lowerStatusFlag(self, flag):
		assert isinstance(flag, jobStatus)
		self.log.debug("lower %s" % (flag))
		self.status &= -1-flag
		self.onEvent(events.job.STATUS_CHANGED, job = self)

	def getStatus(self):
		return self.status

	def getStatusString(self):
		if self.status == 0:
			return _("待機中")
		if self.status & jobStatus.PROCESS_COMPLETE:
			return _("完了")
		if not (self.status & jobStatus.SOURCE_END):
			return _("待機中")
		if not (self.status & jobStatus.CONVERT_STARTED):
			return _("待機中")
		if not (self.status & jobStatus.CONVERT_COMPLETE):
			return _("準備中")
		if not (self.status & jobStatus.PROCESS_STARTED):
			return _("認識待ち")
		else:
			return _("認識中")

	def getId(self):
		return self._id

	#
	# for view
	#
	def __getitem__(self, key):
		if key == 0:
			return self.getName()
		if key == 1:
			return self.getStatusString()
		if key == 2:
			return "%d/%d" % (self.getProcessedCount(), self.getTotalCount())
		if key == 3:
			return type(self._engine).getName()
		raise KeyError

	def __setitem__(self, key, value):
		raise NotImplementedError

	def __len__(self):
		return 4


class virtualAllItemJob(job):
	"""
		App.pyにてリスト先頭にInsertされ、「すべて」として表示される架空のジョブ
	"""

	def __init__(self):
		self._path = None
		self._id = 0
		self._temp = None
		self._name = _("(すべて)")
		self.onEvent = None
		self.log = getLogger("%s.job-%s" % (constants.APP_NAME, self.getId()))
		self.log.info("created job named %s" % (self.getName()))
		self.processedItem = [virtualAllPageItem(self)]
		self.selectedPage = 0

	def getPath(self):
		raise NotImplementedError

	def addCreatedItem(self, item):
		raise NotImplementedError

	def getConvertItem(self):
		raise NotImplementedError

	def addConvertedItem(self, item):
		self.onEvent(events.item.CONVERTED, job = self, item = item)

	def getProcessItem(self):
		raise NotImplementedError

	def addProcessedItem(self, parentJob, item):
		# 全体の中でのインデックスを数えてくる
		# まずは対象ジョブより上に対象ジョブ以外のジョブがあれば、そいつらのページ全部
		idx = 0
		for i in globalVars.jobList:
			if i == parentJob:
				break;
			idx += i.getProcessedCount()
		# 対象ジョブの対象ページより前のページ
		idx += parentJob.getProcessedCount() - 1
		self.processedItem.insert(idx,item)
		self.onEvent(events.item.PROCESSED, job = self, item = item)

	def endSource(self):
		raise NotImplementedError

	def endConvert(self):
		raise NotImplementedError

	def endEngine(self):
		raise NotImplementedError

	def getProcessedCount(self):
		ret = 0
		for job in globalVars.jobList[1:]:
			ret += job.getProcessedCount()
		return ret

	def getTotalCount(self):
		ret = 0
		for job in globalVars.jobList[1:]:
			ret += job.getTotalCount()
		return ret

	def raiseStatusFlag(self, flag):
		raise NotImplementedError

	def lowerStatusFlag(self, flag):
		raise NotImplementedError

	def getStatus(self):
		raise NotImplementedError

	def getStatusString(self):
		raise NotImplementedError

	def __getitem__(self, key):
		# ステータスとエンジン名は表示できない
		if key == 1:
			return ""
		if key == 2:
			return "%d/%d" % (self.getProcessedCount(), self.getTotalCount())
		if key == 3:
			return ""
		return super().__getitem__(key)


class item:
	def __init__(self, path):
		self.path = path
		self.done = False
		self.pageNumber = 1
		self.cursorPos = 0

	def getPath(self):
		return self.path

	def getFormat(self):
		if not hasattr(self, "format"):
			self._register_format()
		return self.format

	def hasGrayScaleFile(self):
		return hasattr(self, "grayScaledPath")

	def setGrayScaleFile(self, path):
		self.grayScaledPath = path

	def getGrayScaleFile(self):
		return self.grayScaledPath

	def _register_format(self):
		ext = os.path.splitext(self.getPath())[1][1:]
		self.format = constants.EXT_TO_FORMAT.get(ext.lower(), constants.FORMAT_UNKNOWN)
		if format == constants.FORMAT_PDF_UNKNOWN:
			# ページ数を確認
			pipeServer = namedPipe.Server(constants.PIPE_NAME)
			pipeServer.start()
			subprocess.run(("pdfinfo", "-enc", "UTF-8", self.getPath(), pipeServer.getFullName()))

			list = pipeServer.getNewMessageList()
			pipeServer.exit()
			m =re.search(r'^ages: *(\d+)',list[0])
			print(m)
			print(m.group(1))
			if int(m.group(1)) > 1:
				self.format = constants.FORMAT_PDF_MULTI_PAGE
				return

			# 単一ページの場合は埋め込みテキストの含まれるPDFであるか判定
			pipeServer = namedPipe.Server(constants.PIPE_NAME)
			pipeServer.start()
			subprocess.run(("pdftotext", "-enc", "UTF-8", self.getPath(), pipeServer.getFullName()))

			list = pipeServer.getNewMessageList()
			pipeServer.exit()
			text = list[0]
			if re.search(r'[^\f\n\r]', text) == None:
				self.format = constants.FORMAT_PDF_TEXT
			else:
				self.format = constants.FORMAT_PDF_IMAGE

	def getCursorPos(self):
		return self.cursorPos

	def getPageNumber(self):
		return self.pageNumber

	def getText(self):
		return self.text

	def isDone(self):
		return self.done

	def setCursorPos(self, pos):
		self.cursorPos = pos

	def setPageNumber(self, pageNumber):
		self.pageNumber = pageNumber

	def setText(self, text):
		self.text = text
		self.done = True

	def __getitem__(self, key):
		if key == 0:
			return _("%dページ" % self.getPageNumber())
		raise KeyError

	def __setitem__(self, key, value):
		raise NotImplementedError

	def __len__(self):
		return 1



class virtualAllPageItem(item):
	def __init__(self, job):
		self.job = job
		self.pageNumber = -1
		self.cursorPos = 0

	def getPath(self):
		raise NotImplementedError

	def getFormat(self):
		raise NotImplementedError

	def hasGrayScaleFile(self):
		raise NotImplementedError

	def setGrayScaleFile(self, path):
		raise NotImplementedError

	def getGrayScaleFile(self):
		raise NotImplementedError

	def _register_format(self):
		raise NotImplementedError

	def setText(self, text):
		raise NotImplementedError

	def getText(self):
		ret = ""
		for item in self.job.getProcessedItems()[1:]:
			ret += item.getText()+"\n"
		return ret

	def isDone(self):
		raise NotImplementedError

	def __getitem__(self, key):
		if key == 0:
			return _("(すべて)")
		raise KeyError

class jobStatus(IntFlag):
	SOURCE_END = auto()
	CONVERT_STARTED = auto()
	CONVERT_COMPLETE = auto()
	PROCESS_STARTED = auto()
	PROCESS_COMPLETE = auto()
