# poppler Command Utility
#Copyright (C) 2019-2023 yamahubuki <itiro.ishino@gmail.com>

import os
import re
import subprocess

import errorCodes

def getInfo(path):
	info = (subprocess.run((os.getcwd() + "/poppler/bin/pdfinfo", "-enc", "UTF-8", path), capture_output=True, text=True, encoding="UTF-8", errors="replace").stdout)
	result = {}
	for line in info.splitlines():
		param = re.split(": +", line, 1)
		result[param[0]] = param[1]
	return result

def split(input, output, page):
	info = (subprocess.run((os.getcwd() + "/poppler/bin/pdfseparate", "-f", str(page), "-l", str(page), input, output), capture_output=True, text=True, encoding="UTF-8", errors="replace").stdout)
	print(info)
	if info.split():
		return (errorCodes.IO_ERROR,info)
	return (errorCodes.OK,"")
