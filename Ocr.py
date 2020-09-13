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
		tmp = pathlib.Path(os.environ["TEMP"]).joinpath("soc")
		if tmp.exists():
			self.tmpDelete(tmp)
		tmp.mkdir()
		result = convert_from_path(path, output_folder=str(tmp), thread_count=os.cpu_count()-1, fmt="png", dpi=400)
		images += result
	# googleのOcr呼び出し
	def google_ocr(self, local_file_path, credential):
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
	def TextSave(self, filePath, text):
		"""ファイル名とテキストを渡すと保存する。"""
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

	def allDelete(self):
		"""変換済みファイルを一層する。"""
		for path in self.saved:
			path.unlink()
		return

	def pdfTextChecker(self, path):
		"""pathに指定されたpdfファイルにテキストが含まれているか判定する。"""
		info = {}
		os.environ["PYTHONIOENCODING"] = "utf-8"
		output = subprocess.check_output(("pdfinfo", path), encoding="cp932")
		lines = output.split("\n")
		for line in lines:
			data = line.split(":", 1)
			if len(data) == 2:
				data[1] = data[1].strip()
			else:
				data.append("")
			info[data[0]] = data[1]
		if info["File size"] != "0 bytes":
			return True
		return False
	def showPdfDialog(self):
		self.qPdfImage = simpleDialog.qDialog(_("pdfからテキストが検出されたため画像に変換して送信します。よろしいですか？"))
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
				if Path.suffix == ".pdf":
					print("きた")
					isText = self.pdfTextChecker(str(Path.resolve()))
					if isText:
						self.qPdfImage = None
						wx.CallAfter(self.showPdfDialog)
						while True:
							if self.qPdfImage is not None:
								break
							time.sleep(0.01)
						if self.qPdfImage == wx.ID_YES:
							print("pdf image convert")
							images = []
							pdfThread = threading.Thread(target = self.tool.pdf_convert, args = (str(Path), images), name = "pdfThread")
							pdfThread.start()
							pdfThread.join()
							file = pathlib.Path(os.environ["temp"]).joinpath("soc/tmp.png")
							text = ""
							count = 0
							for image in images:
								image.save(str(file))
								try:
									text += self.tool.google_ocr(file, self.Credential.credential)
									print(text)
								except(errors.HttpError) as error:
									self.SavedText = ""
									return errorCodes.GOOGLE_ERROR
								del images[count]
								count += 1
							continue
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
		except:
			traceback.print_exc()
			result.append(errorCodes.UNKNOWN)
			pathlib.Path("errorlog.txt").write_text(traceback.format_exc())
			self.allDelete()
		finally:
			wx.CallAfter(dialog.end)
			return