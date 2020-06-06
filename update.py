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
		info = response.text.split("\n")
		self.downLoad = info[0]
		self.version = info[1]
		self.msg = info[2]
		return True
	def run(self, wakeWord):
		path = os.path.abspath(sys.argv[0])
		subprocess.Popen(("up.exe", path, self.download, wakeWord))
		sys.exit()

