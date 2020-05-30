# -*- coding: utf-8 -*-
#app build tool
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
import os
import sys
import subprocess
import shutil
import distutils.dir_util

def runcmd(cmd):
	proc=subprocess.Popen(cmd.split(), shell=True, stdout=1, stderr=2)
	proc.communicate()

if not os.path.exists("locale"):
	print("Error: no locale folder found. Your working directory must be the root of the project. You shouldn't cd to tools and run this script.")

if os.path.isdir("dist\\soc"):
	print("Clearling previous build...")
	shutil.rmtree("dist\\")
	shutil.rmtree("build\\")

print("Building...")
runcmd("pyinstaller soc.py --windowed --log-level=ERROR")

shutil.copytree("tesseract-ocr\\", "dist\\SOC\\tesseract-ocr")
shutil.copytree("poppler\\", "dist\\SOC\\poppler")
shutil.copytree("locale\\","dist\\SOC\\locale", ignore=shutil.ignore_patterns("*.po", "*.pot", "*.po~"))
print("Done!")
