# pdf2text engine

import namedPipe
import os
import subprocess

import constants

from .base import engineBase


class pdf2textEngine(engineBase):
	def __init__(self, ):
		super().__init__("pdf2text")

	def getSupportedFormats(self):
		return constants.FORMAT_PDF_TEXT

	def _recognize(self, item):
		pipeServer = namedPipe.Server(constants.PIPE_NAME_PREFIX + "pdf2textEngine")
		pipeServer.start()
		p = subprocess.Popen((os.getcwd() + "/poppler/bin/pdftotext", "-enc", "UTF-8", item.getPath(), pipeServer.getFullName()))
		text = ""
		while(True):
			text += self._fetchText(pipeServer)
			if p.poll() != None:
				break
		text += self._fetchText(pipeServer)
		pipeServer.exit()
		pipeServer.close()
		item.setText(text)

	def _fetchText(self, pipeServer):
		text = ""
		lst = pipeServer.getNewMessageList()
		if not lst:
			return ""
		for i in lst:
			text += i
		return text

	@classmethod
	def getName(cls):
		return _("PDF埋め込みテキスト抽出")

	@classmethod
	def getSettingDialog(cls):
		return None
