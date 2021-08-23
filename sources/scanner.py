from .base import sourceBase
from jobObjects import job
import globalVars
import time
import os
import shutil
import dtwain
import queue
import errorCodes
import wx
import tempfile

class scannerSource(sourceBase):
	def __init__(self, scannerName, resolution = 300, blankPageDetect = False, isDuplex = False):
		super().__init__("scannerSource")
		self.scannerName = scannerName
		self.resolution = resolution
		self.blankPageDetect = blankPageDetect
		self.isDuplex = isDuplex
		self.scanning = False
		self.running = True
		self.initialized = False
		#self.dtwain_source.raiseDeviceOffline()
		self.temp_dir = tempfile.TemporaryDirectory()
		self.image_tmp = self.temp_dir.name
		self._fileQueue = queue.Queue()

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
		self._nameBase = int(time.time())
		self._pageCount = 0
		self.initialized = True

	def run(self):
		self.dtwain_initialize()
		while True:
			if not self.dtwain_source.isFeederEnabled():
				self._scan()
			if self._isScannerEmpty():
				if self._showMessage(_("スキャナに紙がセットされていません。スキャンを継続しますか？")) == wx.ID_NO:
					break
			self._scan()
			time.sleep(0.01)
		self.running = False

	def _scan(self):
		fileNameList = []
		for i in range(2):
			self._pageCount += 1
			fileName = "%s_%d.png" % (self._nameBase, self._pageCount)
			fileNameList.append(os.path.join(self.image_tmp, fileName))
		self.dtwain_source.acquireFile(fileNameList, dtwain.DTWAIN_PNG)
		for name in fileNameList:
			if os.path.exists(name):
				self._fileQueue.put(job(name))

	def _isScannerEmpty(self):
		if not self.dtwain_source.isFeederLoaded():
			return True
		return False

	def _internal_get_item(self):
		return self._fileQueue.get()

	def getStatus(self):
		status = 0
		if self.running:
			status |= errorCodes.STATUS_SOURCE_LOADING
		else:
			if self._fileQueue.empty():
				status |= errorCodes.STATUS_SOURCE_EMPTY
		if not self._fileQueue.empty():
			status |= errorCodes.STATUS_SOURCE_QUEUED
		return status

	def getStatusString(self):
		if not self.initialized:
			return _("開始中")
		if self.dtwain_source.isAcquiring():
			return _("スキャン中...")
		else:
			return _("大気中...")

	def terminate(self):
		self.temp_dir.cleanup()
