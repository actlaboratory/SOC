import threading
from pdf2image import convert_from_path
import subprocess
import os

def pdfTextChecker(path):
	"""pathに指定されたpdfファイルにテキストが含まれているか判定する。"""
	info = {}
	os.environ["PYTHONIOENCODING"] = "utf-8"
	output = subprocess.check_output(("pdfinfo", path), encoding="cp932")
	lines = output.split("\n")
	for line in lines:
		data = line.split(":", 1)
		if len(data) == 2:
			data[1] = data[1].strip()
		else:
			data.append("")
		info[data[0]] = data[1]
	if info["File size"] != "0 bytes":
		return True
	return False

