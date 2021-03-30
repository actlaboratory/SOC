import errorCodes
import constants
import os
import re
import subprocess
import namedPipe


class job():
	"""OCRの単位のなるクラス。
	処理のもととなるファイル名を持ち実際に処理されるファイルを持ったitemをリストとして保持している。
	"""

	def __init__(self, filename, temporally = True):
		self.filename = filename
		self.temporally = temporally
		self.items = []

	def getFormat(self):
		if not hasattr(self, "format"):
			self._register_format()
		return self.format

	def _register_format(self):
		ext = os.path.splitext(self.filename)[1][1:]
		format = constants.EXT_TO_FORMAT.get(ext.lower(), constants.FORMAT_UNKNOWN)
		if format == constants.FORMAT_PDF_UNKNOWN:
			# 埋め込みテキストの含まれるPDFであるか判定
			pipeServer = namedPipe.Server(constants.PIPE_NAME)
			pipeServer.start()
			subprocess.run(("pdftotext", self.filename, pipeServer.getFullName()))
			list = pipeServer.getNewMessageList()
			pipeServer.exit()
			text = list[0]
			if re.search(r'[^\f\n\r]', text) == None:
				format = constants.FORMAT_PDF_TEXT
			else:
				format = constants.FORMAT_PDF_IMAGE
		self.format = format
		print(hex(format))


class item:
	def __init__(self, filename):
		self.error = False
		self.success = False
		self.filename = filename

	def getErrorString(self):
		if not self.error:
			return ""
		return self.errorMessage

	def setSuccess(self, text):
		self.text = text
		self.success = True

	def getText(self):
		return self.text

	def setError(self, message):
		self.error = True
		self.errorMessage = message
		self.done = True

