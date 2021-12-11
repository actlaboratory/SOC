from .base import sourceBase
import globalVars
import time
import os
import shutil
import dtwain
import errorCodes
import jobObjects

class scannerSource(sourceBase):
	def __init__(self, scannerName, resolution = 400, blankPageDetect = False, isDuplex = False):
		super().__init__("scannerSource")
		self.scannerName = scannerName
		self.resolution = resolution
		self.blankPageDetect = blankPageDetect
		self.isDuplex = isDuplex
		self.scanning = False
		self.running = True
		self.initialized = False
		#self.dtwain_source.raiseDeviceOffline()
		self.image_tmp = globalVars.app.getTmpDir()

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

	def _run(self):
		self.dtwain_initialize()
		job = jobObjects.job()
		self.onJobCreated(job)
		while True:
			if not self.dtwain_source.isFeederEnabled():
				self._scan(job)
			if self._isScannerEmpty():
				break
			self._scan(job)
			time.sleep(0.01)
		job.endSource()
		self.running = False

	def _scan(self, job:jobObjects.job):
		fileNameList = []
		for i in range(2):
			self._pageCount += 1
			fileName = "%s_%d.png" % (self._nameBase, self._pageCount)
			fileNameList.append(os.path.join(self.image_tmp, fileName))
		self.dtwain_source.acquireFile(fileNameList, dtwain.DTWAIN_PNG)
		for name in fileNameList:
			if os.path.exists(name):
				job.addCreatedItem(jobObjects.item(name))

	def _isScannerEmpty(self):
		if not self.dtwain_source.isFeederLoaded():
			return True
		return False

	def _final(self):
		self.dtwain_source.close()
