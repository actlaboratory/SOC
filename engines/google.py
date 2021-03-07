import os
import CredentialManager
from apiclient import discovery
import errorCodes
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient import errors
import io
from .base import engineBase

class googleEngine(engineBase):
	def __init__(self):
		super().__init__("google")
		self.credential = CredentialManager.CredentialManager(True)
		self.credential.Authorize()
		print("authorize success")
		self._statusString = ("大気中...")

	def getSupportedType(self):
		return (errorCodes.TYPE_JPG, errorCodes.TYPE_PNG, errorCodes.TYPE_GIF, errorCodes.TYPE_PDF_IMAGE_ONLY)

	def _recognize(self, item):
		print("recognize")
		self._statusString = _("認識開始")
		service = discovery.build("drive", "v3", credentials=self.credential.credential)
		with open(item.fileName, mode = "rb") as f:
			self._statusString = _("アップロード中")
			media_body = MediaIoBaseUpload(f, mimetype="application/vnd.google-apps.document", resumable=True)
			req_body = {
				"name": os.path.basename(item.fileName),
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
		item.setSuccess(stream.getvalue().decode("utf-8"))
		self._statusString = _("大気中")

	def getStatusString(self):
		return self._statusString

