#Soc OCR module
#Copyright (C) 2020 guredora <contact@guredora.com>

import globalVars
from PIL import Image
import pyocr
import constants
import pyocr.builders
from pdf2image import convert_from_path
import pathlib
import sys
import errorCodes
import CredentialManager
import simpleDialog
from PIL import UnidentifiedImageError
import httplib2
from apiclient import discovery
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient import errors
import io
import os
import threading
import time
import wx
import traceback
import subprocess
import util
import pdfUtil

class OcrTool():
	def __init__(self):
		self.available_language=("jpn", "jpn_fast", "jpn_vert", "jpn_vert_fast")#tesseract-ocrの設定の保存

	def google_ocr(self, local_file_path, credential, pdf_to_png = False, dialog=None):
		if local_file_path.suffix == ".pdf" and pdf_to_png:
			text = ""
			file = pathlib.Path(globalVars.app.tmpdir).joinpath("tmp.png")
			images = pdfUtil.pdf_to_image(str(local_file_path))
			for image in images:
				if dialog is not None and dialog.cancel:
					return ""
				image.save(str(file))
				text += self.google_ocr(file, credential)
			return text
		service = discovery.build("drive", "v3", credentials=credential)
		with local_file_path.open("rb") as f:
			media_body = MediaIoBaseUpload(f, mimetype="application/vnd.google-apps.document", resumable=True)
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
			images = pdfUtil.pdf_to_image(local_file_path)
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
		self.pdf_to_png = False
		os.environ["PATH"] += os.pathsep + os.getcwd() + "/poppler/bin"

	def _allDelete(self):
		"""変換済みファイルを一層する。"""
		for path in self.saved:
			path.unlink()
		return

	def ocr_exe(self, dialog):
		"""ocrを実行する。"""
		if self.Engine == 0:
			try:
				self.Credential = CredentialManager.CredentialManager(True)
			except:
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
			wx.CallAfter(dialog.changeName, (Path.name))
			if self.Engine == 0:#googleの呼び出し
				if not self.Credential.isOK():
					self.SavedText = ""
					return errorCodes.NOT_AUTHORIZED
				self.Credential.Authorize()
				try:
					text = self.tool.google_ocr(Path, self.Credential.credential, self.pdf_to_png, dialog)
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
			util.textSave(Path.with_suffix(".txt"), text)#ファイルに保存
			self.saved.append(Path.with_suffix(".txt"))
			self.SavedText += text
		return errorCodes.OK
	def lapped_ocr_exe(self, dialog, result):
		try:
			result.append(self.ocr_exe(dialog))
		except:
			traceback.print_exc()
			result.append(errorCodes.UNKNOWN)
			pathlib.Path("errorlog.txt").write_text(traceback.format_exc())
			self.allDelete()
		finally:
			wx.CallAfter(dialog.end)
			return