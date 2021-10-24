import os
import CredentialManager
from apiclient import discovery
import errorCodes
import constants
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient import errors
import io
from .base import engineBase


class googleEngine(engineBase):
	_engineName = "google"

	def __init__(self):
		super().__init__("google")

	def _init(self):
		self.credential = CredentialManager.CredentialManager(True)
		if not self.credential.isOK():
			self.log.error("credential not authorized")
		self.credential.Authorize()

	def getSupportedFormats(self):
		return constants.FORMAT_JPEG | constants.FORMAT_PNG | constants.FORMAT_GIF|constants.FORMAT_PDF_IMAGE

	def _recognize(self, item):
		service = discovery.build("drive", "v3", credentials=self.credential.credential)
		with open(item.getPath(), mode = "rb") as f:
			self.log.info("uploading...")
			media_body = MediaIoBaseUpload(f, mimetype="application/vnd.google-apps.document", resumable=True)
			req_body = {
				"name": os.path.basename(item.getPath()),
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
		while done is False:
			status, done = downloader.next_chunk()
		service.files().delete(fileId=ID).execute()
		item.setText(stream.getvalue().decode("utf-8"))

