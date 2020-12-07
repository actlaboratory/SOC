import os
from apiclient import discovery
import errorCodes
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient import errors
import io

class engineBase(object):
	"""すべてのエンジンクラスが継承する基本クラス。"""
	def __init__(self):
		self.cancel = False

	def recognition(self, filePath, statusContainer):
		raise NotImplementedError()

	def getSupportedType(self):
		raise NotImplementedError()

	def cancel(self):
		self.cancel = True

class googleEngine(engineBase):
	def __init__(self):
		super().__init__()
		self.credential = None

	def setCredential(self, credential):
		self.credential = credential

	def getSupportedType(self):
		return (errorCodes.TYPE_JPG, errorCodes.TYPE_PNG, errorCodes.TYPE_GIF, errorCodes.TYPE_PDF_IMAGE_ONLY)

	def recognition(self, filePath, statusContainer):
		if self.cancel:
			statusContainer.cancel()
			return
		service = discovery.build("drive", "v3", credentials=credential)
		with open(filePath, mode = "rb") as f:
			media_body = MediaIoBaseUpload(f, mimetype="application/vnd.google-apps.document", chunksize = 64*1024, resumable=True)
				file = service.files().create(
				body = {
					"name": os.path.basename(filePath),
					"mimeType":"application/vnd.google-apps.document"
				},
				media_body = media_body,
				ocrLanguage = "ja",
				fields="id"
			).execute()
		ID = file.get("id")
		request = service.files().export_media(fileId=ID, mimeType = "text/plain")
		stream = io.bytesIo()
		downloader = MediaIoBaseDownload(stream, request)
		done = False
		while done is False:
			status, done = downloader.next_chunk()
		service.files().delete(fileId=ID).execute()
		statusContainer.success(stream.getValue().decode("utf-8")

class tesseractEngine(engineBase):
	def __init__(self, mode):
		super().__init__()
		self.mode = mode

	def getSupportedType(self):
		return (errorCodes.TYPE_JPG, errorCodes.TYPE_PNG, errorCodes.TYPE_GIF, errorCodes.TYPE_BMP)

	def recognition(self, filePath, statusContainer):
		if self.cancel:
			statusContainer.cancel()
			return
		tools = pyocr.get_available_tools()
		tool = tools[0]
		text = tool.image_to_string(
			Image.open(filePath),
			lang = self.mode,
			builder = pyocr.builders.TextBuilder()
		)
		statusContainer.success(text)
