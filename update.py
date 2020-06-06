# アップデート関連プログラム
#Copyright (C) 2020 guredora <contact@guredora.com>

import requests
import subprocess

class update():
	def check(self, app_name, current_version, check_url):
		url = "%s?name=%s&version=%s" % (check_url, app_name, current_version)# 引数からURLを生成
		response = requests.get(url)# サーバーに最新バージョンを問い合わせる
		if response.text == "latest":
			return False
		info = response.text.sprit("\n")
		self.downLoad = info[0]
		self.version = info[1]
		self.msg = info[1]
		return True
	def run(self, path, wakeWord):
		subprocess.Popen(("up.exe", self.download, wakeWord))
		sys.exit()

