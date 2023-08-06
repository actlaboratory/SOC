# poppler Command Utility
#Copyright (C) 2019-2023 yamahubuki <itiro.ishino@gmail.com>

import os
import re
import subprocess

def getInfo(path):
	info = (subprocess.run((os.getcwd() + "/poppler/bin/pdfinfo", "-enc", "UTF-8", path), capture_output=True, text=True, encoding="UTF-8", errors="replace").stdout)
	result = {}
	for line in info.splitlines():
		param = re.split(": +", line, 1)
		result[param[0]] = param[1]
	return result
