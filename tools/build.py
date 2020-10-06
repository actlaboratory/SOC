# -*- coding: utf-8 -*-
#app build tool
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
import glob
import os
import sys
import subprocess
import shutil
import distutils.dir_util
import PyInstaller
import diff_archiver
import hashlib
import json

def runcmd(cmd):
	proc=subprocess.Popen(cmd.split(), shell=True, stdout=1, stderr=2)
	proc.communicate()

appveyor=False
BASE_PACKAGE_URL="https://github.com/actlaboratory/SOC/releases/download/0.0.5/SOC-0.0.5.zip"

if len(sys.argv)==2 and sys.argv[1]=="--appveyor":
	appveyor=True

print("Starting build (appveyor mode=%s)" % appveyor)
build_filename=os.environ['APPVEYOR_REPO_TAG_NAME'] if 'APPVEYOR_REPO_TAG_NAME' in os.environ else 'snapshot'
print("Will be built as %s" % build_filename)

pyinstaller_path="pyinstaller.exe" if appveyor is False else "%PYTHON%\\Scripts\\pyinstaller.exe"
hooks_path = os.path.join(PyInstaller.__path__[0], "hooks/")
print("hooks_path is %s" % (hooks_path))
print("pyinstaller_path=%s" % pyinstaller_path)
if not os.path.exists("locale"):
	print("Error: no locale folder found. Your working directory must be the root of the project. You shouldn't cd to tools and run this script.")

if os.path.isdir("dist\\soc"):
	print("Clearling previous build...")
	shutil.rmtree("dist\\")
	shutil.rmtree("build\\")

print("Building...")
shutil.copy("tools/hook-googleapiclient.py", hooks_path)
runcmd("%s --windowed --log-level=ERROR soc.py" % pyinstaller_path)

shutil.copytree("tesseract-ocr\\", "dist\\SOC\\tesseract-ocr")
shutil.copytree("poppler\\", "dist\\SOC\\poppler")
shutil.copytree("locale\\","dist\\SOC\\locale", ignore=shutil.ignore_patterns("*.po", "*.pot", "*.po~"))
for elem in glob.glob("public\\*"):
	if os.path.isfile(elem):
		shutil.copyfile(elem,"dist\\SOC\\%s" % os.path.basename(elem))
	else:
		shutil.copytree(elem,"dist\\SOC\\%s" % os.path.basename(elem))
#end copypublic

if os.path.exists("release"):
	print("packaging release file...")
	for file in os.listdir("release"):
		shutil.copy(os.path.join("release", file), "dist/soc")
print("Compressing into package...")
shutil.make_archive("SOC-%s" % (build_filename),'zip','dist')

if build_filename=="snapshot":
	print("Skipping batch archiving because this is a snapshot release.")
else:
	print("Making patch...")
	archiver=diff_archiver.DiffArchiver(BASE_PACKAGE_URL,"SOC-%s.zip" % (build_filename),"SOC-%spatch" % (build_filename),clean_base_package=True, skip_root = True)
	archiver.work()
	print("creating version info file...")
	with open("SOC-%s.zip" % (build_filename), mode = "rb") as f:
		content = f.read()
		package_hash = hashlib.sha1(content).hexdigest()
	with open("SOC-%spatch.zip" % (build_filename), mode = "rb") as f:
		content = f.read()
		patch_hash = hashlib.sha1(content).hexdigest()
	with open("soc-%s_info.json" % (build_filename), mode = "w") as f:
		info = {
			"package_hash": package_hash,
			"patch_hash": patch_hash
		}
		json.dump(info, f)
print("Build finished!")
