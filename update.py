# アップデート関連プログラム
#Copyright (C) 2020 guredora <contact@guredora.com>

import requests
import subprocess
import errorCodes
import ConfigManager
import os
import pathlib
import sys

class update():
	def check(self, app_name, current_version, check_url):
		url = "%s?name=%s&updater_version=1.0.0&version=%s" % (check_url, app_name, current_version)# 引数からURLを生成
		try:
			response = requests.get(url)# サーバーに最新バージョンを問い合わせる
		except requests.exceptions.ConnectionError as c:
			return errorCodes.NET_ERROR
		if not response.status_code == 200:
			print(response.status_code)
			return errorCodes.NET_ERROR
		json = response.json()
		code = json["code"]
		print(code)
		if code == errorCodes.UPDATER_NEED_UPDATE:
			self.download = json["updater_url"]
			self.version = json["update_version"]
			self.description = json["update_description"]
		if code == errorCodes.UPDATER_VISIT_SITE:
			self.URL = json["URL"]
			self.description = json["info_description"]
		return code
	def run(self, wakeWord):
		path = os.path.abspath(sys.argv[0])
		response = requests.get(self.download)
		up_name = os.path.basename(self.download)
		pathlib.Path(up_name).write_bytes(response.content)
		subprocess.Popen(("up.exe", path, up_name, wakeWord))
		sys.exit()

