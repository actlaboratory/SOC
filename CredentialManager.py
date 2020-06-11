#Google credential manager
#Copyright (C) 2020 guredora <contact@guredora.com>
import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
import constants
import errorCodes

import google.auth.transport.requests

class CredentialManager:

	def __init__(self, need_refresh=False):
		self.credential = None
		#パスを求めておく
		credential_dir = constants.GOOGLE_DIR
		self.credentialPath = os.path.join(credential_dir,constants.GOOGLE_FILE_NAME)

		#ディレクトリがなければ作る
		if not os.path.exists(credential_dir):
			os.makedirs(credential_dir)

		#ファイルがあれば読み込む
		if os.path.isfile(self.credentialPath):
			try:
				self.credential=Credentials.from_authorized_user_file(self.credentialPath,scopes=constants.GOOGLE_NEED_SCOPES)
				if need_refresh:
					self.refresh()
			except ValueError:
				pass

	def isOK(self):
		return not self.credential==None

	def MakeFlow(self):
		self.flow = InstalledAppFlow.from_client_config(
			json.loads(constants.GOOGLE_CLIENT_SECRET),
			scopes=constants.GOOGLE_NEED_SCOPES
		)
		url = self.flow.prepare_run_local_server(
			host='localhost',
			port=8080, 
			authorization_prompt_message='',			#標準出力への表示は不要
			success_message=_("googleでの認証手続きが完了しました。このブラウザを閉じ、処理結果を確認してください。<script>window.close();</script>"),
			open_browser=False
		)
		return url

	def getCredential(self):
		credentials=self.flow.run_local_server()
		if credentials==None:
			return errorCodes.WAITING_USER
		if credentials==False:
			return errorCodes.NOT_AUTHORIZED
		try:
			with open(self.credentialPath,mode="w") as f:
				f.write(credentials.to_json())
		except:
			return errorCodes.IO_ERROR
		self.credentials=credentials
		return errorCodes.OK

	def refresh(self):
		request = google.auth.transport.requests.Request()
		self.credential.refresh(request)

	def Authorize(self):
		if self.credential.expired:
			self.refresh()
		self.header = {}
		self.credential.apply(self.header)

