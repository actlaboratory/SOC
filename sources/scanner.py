from sources import base
from fileContainer import container
import globalVars
import time
import os
import shutil
import dtwain
import queue
import errorCodes

class scannerSource(base.sourceBase):
	def __init__(self, scannerName, resolution = 300, blankPageDetect = False, isDuplex = False):
		super().__init__()
		self.scannerName = scannerName
		self.resolution = resolution
		self.blankPageDetect = blankPageDetect
		self.isDuplex = isDuplex
		self.scanning = False
		self.running = True
		self.initialized = False
		#self.dtwain_source.raiseDeviceOffline()
		self.image_tmp = os.path.join(globalVars.app.tmpdir, "acquiredImage")
		if os.path.exists(self.image_tmp):
			shutil.rmtree(self.image_tmp)
		os.mkdir(self.image_tmp)
		self.fileQueue = queue.Queue()

	def dtwain_initialize(self):
		self.dtwain = dtwain.dtwain(True)
		self.dtwain_source = self.dtwain.getSourceByName(self.scannerName)
		self.dtwain_source.setResolution(self.resolution)
		if self.blankPageDetect:
			self.log.info("Blank page detection enabled")
			self.dtwain_source.setBlankPageDetection(99.5)
		if self.dtwain_source.isDuplexSupported():
			self.log.info(f'set duplex mode = {self.isDuplex}')
			self.dtwain_source.enableDuplex(self.isDuplex)
		if self.dtwain_source.isDuplexEnabled():
			self.log.info("duplex scanning enabled")
		#if self.dtwain_source.isPaperDetectable():
			#self.log.info("this scanner is paper detectable")
		self.nameBase = int(time.time())
		self.pageCount = 0
		self.initialized = True

	def run(self):
		self.dtwain_initialize()
		while True:
			if not self.dtwain_source.isFeederEnabled():
				self.scan()
			if self.isScannerEmpty():
				break
			self.scan()
			time.sleep(0.01)
		self.running = False

	def scan(self):
		fileNameList = []
		for i in range(2):
			self.pageCount += 1
			fileName = "%s_%d.png" % (self.nameBase, self.pageCount)
			fileNameList.append(os.path.join(self.image_tmp, fileName))
		self.dtwain_source.acquireFile(fileNameList, dtwain.DTWAIN_PNG)
		for name in fileNameList:
			if os.path.exists(name):
				self.fileQueue.put(container(name))

	def isScannerEmpty(self):
		if not self.dtwain_source.isFeederLoaded():
			return True
		return False

	def get(self):
		return self.fileQueue.get()

	def getStatus(self):
		status = 0
		if self.running:
			status |= errorCodes.STATUS_SOURCE_LOADING
		else:
			if self.fileQueue.empty():
				status |= errorCodes.STATUS_SOURCE_EMPTY
		if not self.fileQueue.empty():
			status |= errorCodes.STATUS_SOURCE_QUEUED
		return status

	def getStatusString(self):
		if not self.initialized:
			return _("開始中")
		if self.dtwain_source.isAcquiring():
			return _("スキャン中...")
		else:
			return _("大気中...")
