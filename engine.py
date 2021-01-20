import os
import CredentialManager
from apiclient import discovery
import errorCodes
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient import errors
import io
import pyocr
from PIL import Image

class engineBase(object):
	"""すべてのエンジンクラスが継承する基本クラス。"""
	def __init__(self):
		self.interrupt = False
		self.processingContainer = []

	def recognition(self, container):
		raise NotImplementedError()

	def getSupportedType(self):
		raise NotImplementedError()

	def setInterrupt(self):
		self.interrupt = True

	def getStatusString(self):
		return _("未定義")

class googleEngine(engineBase):
	def __init__(self):
		super().__init__()
		self.credential = CredentialManager.CredentialManager(True)
		if not self.credential.isOK():
			return errorCodes.NOT_AUTHORIZED
		self.credential.Authorize()
		self._statusString = ("大気中...")

	def getSupportedType(self):
		return (errorCodes.TYPE_JPG, errorCodes.TYPE_PNG, errorCodes.TYPE_GIF, errorCodes.TYPE_PDF_IMAGE_ONLY)

	def recognition(self, container):
		if self.interrupt:
			container.setInterrupt()
			return
		self.processingContainer.append(container)
		self._statusString = _("認識開始")
		service = discovery.build("drive", "v3", credentials=self.credential.credential)
		with open(container.fileName, mode = "rb") as f:
			self._statusString = _("アップロード中")
			media_body = MediaIoBaseUpload(f, mimetype="application/vnd.google-apps.document", resumable=True)
			req_body = {
				"name": os.path.basename(container.fileName),
				"mimeType":"application/vnd.google-apps.document"
			}
			file = service.files().create(
				body = req_body,
				media_body = media_body,
				ocrLanguage = "ja",
				fields="id"
			).execute()
		ID = file.get("id")
		request = service.files().export_media(fileId=ID, mimeType = "text/plain")
		stream = io.BytesIO()
		downloader = MediaIoBaseDownload(stream, request)
		done = False
		self._statusString = _("ダウンロード中")
		while done is False:
			status, done = downloader.next_chunk()
		service.files().delete(fileId=ID).execute()
		container.setSuccess(stream.getvalue().decode("utf-8"))
		self.processingContainer.remove(container)
		self._statusString = _("大気中")

	def getStatusString(self):
		return self._statusString

class tesseractEngine(engineBase):
	def __init__(self, mode):
		super().__init__()
		self.mode = mode
		tools = pyocr.get_available_tools()
		self.tesseract = tools[0]
		self._statusString = _("大気中")

	def getSupportedType(self):
		return (errorCodes.TYPE_JPG, errorCodes.TYPE_PNG, errorCodes.TYPE_GIF, errorCodes.TYPE_BMP)

	def recognition(self, container):
		if self.interrupt:
			container.setInterrupt()
			return
		self.processingContainer.append(container)
		self._statusString = _("認識開始")
		text = self.tesseract.image_to_string(
			Image.open(container.fileName),
			lang = self.mode,
			builder = pyocr.builders.TextBuilder()
		)
		container.setSuccess(text)
		self.processingContainer.remove(container)
		self._statusString = _("大気中")

	def getStatusString(self):
		return self._statusString
