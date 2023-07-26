from askEvent import askEventBase
from .base import sourceBase, sourceAskEvent
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
		if self.dtwain_source.isFeederEnabled():
			self.log.info("using feeder enable scanner")
			self._scan_feeder_enabled()
		else:
			self.log.info("using feeder disable scanner")
			self._scan_feeder_disabled()
		self.running = False

	def _scan_feeder_disabled(self):
		job = jobObjects.job(None, True, self, self.engine)
		self.onJobCreated(job)
		while True:
			time.sleep(0.01)
			self._scan(job)
			res = self.ask(scanContinueNotFeeder)
			if res == scanContinueNotFeeder._SCAN_NOT_CONTINUE:
				break
			elif res == scanContinueNotFeeder._SCAN_CONTINUE_NEW_FILE:
				job.endSource()
				job = jobObjects.job(None, True, self, self.engine)
				self.onJobCreated(job)
				continue
			elif res == scanContinueNotFeeder._SCAN_CONTINUE:
				continue
		job.endSource()
		self.log.info("scan completed")

	def _scan_feeder_enabled(self):
		job_created = False
		while True:
			if self._isScannerEmpty():
				if job_created:
					res = self.ask(scanContinue)
					if res == scanContinue._SCAN_NOT_CONTINUE:break
					elif res == scanContinue._SCAN_CONTINUE:continue
					elif res == scanContinue._SCAN_CONTINUE_NEW_FILE:
						job.endSource()
						job = jobObjects.job(None, True, self, self.engine)
						self.onJobCreated(job)
				else:
					res = self.ask(scannerNoPaper)
					if res == scannerNoPaper._CANCEL:break
				continue
			if not job_created:
				job = jobObjects.job(None, True, self, self.engine)
				self.onJobCreated(job)
				job_created = True
			self._scan(job)
		if job_created:job.endSource()
		self.log.info("scanned all paper with feeder.")

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

class scannerAskEvent(sourceAskEvent):
	_title = _("スキャナ")

class scanContinue(scannerAskEvent):
	_SCAN_CONTINUE = 1
	_SCAN_CONTINUE_NEW_FILE = 2
	_SCAN_NOT_CONTINUE = 3
	_message = _("スキャナの紙がなくなりました。新しい髪をセットしてスキャンを続けますか？")
	_selection_to_result = {
		_("現在のファイルに追記"): _SCAN_CONTINUE,
		_("別ファイルで続ける"): _SCAN_CONTINUE_NEW_FILE,
		_("終了"): _SCAN_NOT_CONTINUE
	}

class scanContinueNotFeeder(scanContinue):
	_message = _("スキャンが終了しました。続けてスキャンを行いますか？")

class scannerNoPaper(scannerAskEvent):
	_OK = 1
	_CANCEL = 2
	_message = _("スキャナに紙がセットされていません。紙をセットしなおしてOKボタンを押してください。")
	_selection_to_result = {
		_("OK"): _OK,
		_("キャンセル"): _CANCEL
	}
