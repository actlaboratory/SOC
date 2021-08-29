# -*- coding: utf-8 -*-
#Application startup file
#Copyright (C) 2020 guredora <contact@guredora.com>

import os
import sys
import simpleDialog
import traceback

#カレントディレクトリを設定
if hasattr(sys,"frozen"): os.chdir(os.path.dirname(sys.executable))
else: os.chdir(os.path.abspath(os.path.dirname(__file__)))

def exchandler(type, exc, tb):
	msg=traceback.format_exception(type, exc, tb)
	print("".join(msg))
	try:
		f=open("errorLog.txt", "a")
		f.writelines(msg)
		f.close()
	except:
		pass
	simpleDialog.winDialog("error", "An error has occured. Contact to the developer for further assistance. Detail:" + "\n".join(msg[-2:]))
	os._exit(1)

sys.excepthook=exchandler

import win32timezone#ダミー
def _(string): pass#dummy

#dllを相対パスで指定した時のため、カレントディレクトリを変更
os.chdir(os.path.dirname(os.path.abspath(__file__)))
#Python3.8対応
#dllやモジュールをカレントディレクトリから読み込むように設定
if sys.version_info.major>=3 and sys.version_info.minor>=8:
	os.add_dll_directory(os.path.dirname(os.path.abspath(__file__)))
	sys.path.append(os.path.dirname(os.path.abspath(__file__)))


import app as application
import constants
import globalVars

def main():
	if os.path.exists("errorLog.txt"):
		try:
			os.remove("errorLog.txt")
		except:
			pass
	app=application.Main()
	globalVars.app=app
	result = app.initialize()
	if not result:
		return
	app.MainLoop()
	app.config.write()


if __name__ == "__main__": main()
