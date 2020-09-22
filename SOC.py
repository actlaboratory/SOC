# -*- coding: utf-8 -*-
#Application startup file
#Copyright (C) 2020 guredora <contact@guredora.com>

import win32timezone#ダミー
def _(string): pass#dummy

#dllを相対パスで指定した時のため、カレントディレクトリを変更
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
#Python3.8対応
#dllやモジュールをカレントディレクトリから読み込むように設定
import sys
if sys.version_info.major>=3 and sys.version_info.minor>=8:
	os.add_dll_directory(os.path.dirname(os.path.abspath(__file__)))
	sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import traceback
import app as application
import constants
import globalVars

def main():
	app=application.Main()
	globalVars.app=app
	result = app.initialize()
	if not result:
		return
	app.MainLoop()
	app.config.write()

def exchandler(type, exc, tb):
	msg=traceback.format_exception(type, exc, tb)
	print("".join(msg))
	f=open("errorLog.txt", "a")
	f.writelines(msg)
	f.close()

#global schope
sys.excepthook=exchandler

if __name__ == "__main__": main()
