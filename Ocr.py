#Soc OCR module
#Copyright (C) 2020 guredora <contact@guredora.com>

import globalVars
from PIL import Image
import pyocr
import pyocr.builders
from pdf2image import convert_from_path
import pathlib
import errorCodes
import CredentialManager
from PIL import UnidentifiedImageError
import httplib2
from apiclient import discovery
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient import errors
import io
import os
import threading
import wx
import traceback

class OcrTool():
	def __init__(self):
		self.available_language=("jpn", "jpn_fast", "jpn_vert", "jpn_vert_fast")#tesseract-ocrの設定の保存
	#folderの内容をすべて削除
	def tmpDelete(self, tmp):
		for path in tmp.iterdir():
			if path.is_dir():
				self.tmpDelete(path)
			if path.is_file:
				path.unlink()
		tmp.rmdir()
		return
	# pdfを画像に変換する
	def pdf_convert(self, path, images):
		tmp = pathlib.Path(os.environ["TEMP"]).joinpath("OcrTool")
		if tmp.exists():
			self.tmpDelete(tmp)
		tmp.mkdir()
		result = convert_from_path(path, output_folder=str(tmp), thread_count=os.cpu_count()-1, fmt="png", dpi=400)
		images += result
	# googleのOcr呼び出し
	def google_ocr(self, local_file_path, credential):
		service = discovery.build("drive", "v3", credentials=credential)
		media_body = MediaFileUpload(local_file_path, mimetype="application/vnd.google-apps.document", resumable=True)
		file = service.files().create(
				body = {
					"name": local_file_path.name,
					"mimeType":"application/vnd.google-apps.document"
				},
				media_body = media_body,
				ocrLanguage = "ja",
				fields="id"
			).execute()
		ID = file.get("id")
		request = service.files().export_media(fileId=ID, mimeType = "text/plain")
		fh = io.BytesIO()
		downloader = MediaIoBaseDownload(fh, request)
		done = False
		while done is False:
			status, done = downloader.next_chunk()
		service.files().delete(fileId=ID).execute()
		return fh.getvalue().decode("utf-8")
	# tesseract-ocrの呼び出し
	def tesseract_ocr(self, local_file_path, number, dialog):
		lang = self.available_language[number]
		text = ""
		tools = pyocr.get_available_tools()
		tool = tools[0]
		if local_file_path.suffix == ".pdf":
			images = []
			pdfThread = threading.Thread(target = self.pdf_convert, args = (str(local_file_path), images), name = "pdfThread")
			pdfThread.start()
			pdfThread.join()
			i = 0
			for image in images:
				if dialog.cancel:
					return
				text += tool.image_to_string(
				image,
				lang = lang,
				builder = pyocr.builders.TextBuilder())
				del images[i]
				i+=1
			return text
		text = tool.image_to_string(
		Image.open(local_file_path.resolve()),
		lang = lang,
		builder = pyocr.builders.TextBuilder())
		return text

class OcrManager():
	def __init__(self):
		self.saved = []
		self.SavedText = ""
		self.OcrList = []
		self.Engine = -1
		self.mode = -1
		self.tool = OcrTool()
		os.environ["PATH"] += os.pathsep + os.getcwd() + "/poppler/bin"
	# ファイル名とテキストを渡すと保存する関数
	def TextSave(self, filePath, text):
		if isinstance(filePath, pathlib.WindowsPath):
			filePath.write_text(text, encoding="utf-8")
			txt = filePath.read_text(encoding="utf-8")
			self.saved.append(filePath)
			self.SavedText += text
			return
		pathlib.Path(filePath).write_text(text, encoding="utf-8")
		self.saved.append(filePath)
		self.SavedText += text
		return

	def allDelete(self):#変換済みファイルを一掃する
		for path in self.saved:
			path.unlink()
		return
	# Ocrの実行
	def ocr_exe(self, dialog):
		if self.Engine == 0:
			try:
				self.Credential = CredentialManager.CredentialManager(True)
			except Exception:
				return errorCodes.NET_ERROR#ネットワーク関係のエラー
		for Path in self.OcrList:
			if dialog.cancel:#キャンセル処理
				self.allDelete()
				self.SavedText = ""
				return errorCodes.CANCELED
			if not Path.exists():#ファイルがなかった場合
				self.allDelete()
				self.SavedText = ""
				return errorCodes.FILE_NOT_FOUND
			wx.CallAfter(dialog.changeName, (Path.stem))
			if self.Engine == 0:#googleの呼び出し
				if not self.Credential.isOK():
					self.SavedText = ""
					return errorCodes.NOT_AUTHORIZED
				self.Credential.Authorize()
				try:
					text = self.tool.google_ocr(Path, self.Credential.credential)
				except(errors.HttpError) as error:
					self.SavedText = ""
					return errorCodes.GOOGLE_ERROR
			if self.Engine == 1:#tesseractの呼び出し
				try:
					text = self.tool.tesseract_ocr(Path, self.mode, dialog)
				except(UnidentifiedImageError):
					self.allDelete()
					self.SavedText = ""
					return errorCodes.FILE_NOT_SUPPORTED
			if text == None:
				self.allDelete()
				self.SavedText = ""
				return errorCodes.CANCELED
			self.TextSave(Path.with_suffix(".txt"), text)#ファイルに保存
		return errorCodes.OK
	def lapped_ocr_exe(self, dialog, result):
		try:
			result.append(self.ocr_exe(dialog))
		except exception as c:
			result.append(errorCodes.UNKNOWN)
			pathlib.Path("errorlog.txt").write_text(traceback.format_exc())
		finally:
			wx.CallAfter(dialog.end)
			return