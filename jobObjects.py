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

class job():
	"""OCRの単位のなるクラス。
	処理のもととなるファイル名を持ち実際に処理されるファイルを持ったitemをリストとして保持している。
	"""

	def __init__(self, fileName, temporally = True):
		self.fileName = fileName
		self.temporally = temporally
		self.items = []

	def getItems(self):
		return self.items

	def appendItem(self, item):
		self.items.append(item)

	def getFormat(self):
		if not hasattr(self, "format"):
			self._register_format()
		return self.format

	def _register_format(self):
		ext = os.path.splitext(self.getFileName)[1][1:]
		format = constants.EXT_TO_FORMAT.get(ext.lower(), constants.FORMAT_UNKNOWN)
		if format == constants.FORMAT_PDF_UNKNOWN:
			# 埋め込みテキストの含まれるPDFであるか判定
			pipeServer = namedPipe.Server(constants.PIPE_NAME)
			pipeServer.start()
			subprocess.run(("pdftotext", self.getFileName(), pipeServer.getFullName()))
			list = pipeServer.getNewMessageList()
			pipeServer.exit()
			text = list[0]
			if re.search(r'[^\f\n\r]', text) == None:
				format = constants.FORMAT_PDF_TEXT
			else:
				format = constants.FORMAT_PDF_IMAGE
		self.format = format

	def getAllItemText(self):
		text = ""
		for item in self.items:
			text += item.getText()
			if text[-1] != "\n":
				text += "\n"
		return text

	def getFileName(self):
		return self.fileName

class item:
	def __init__(self, fileName):
		self.fileName = fileName

	def setText(self, text):
		self.text = text

	def getText(self):
		return self.text

	def getFileName(self):
		return self.fileName
