import threading
from pdf2image import convert_from_path
import subprocess
import os
import util
import pathlib
import globalVars
import namedPipe
import constants
import simpleDialog
import re

pattern = re.compile(r'[^\f\n\r]')

def getPdfInfo(path):
	if not pathlib.Path(path).suffix == ".pdf":
		return False
	info = {}
	os.environ["PYTHONIOENCODING"] = "utf-8"
	output = subprocess.check_output(("pdfinfo", path)).decode("utf-8", errors="replace")
	lines = output.split("\n")
	for line in lines:
		data = line.split(":", 1)
		if len(data) == 2:
			data[1] = data[1].strip()
		else:
			data.append("")
		info[data[0]] = data[1]
	return info

def pdfTextChecker(path):
	if not pathlib.Path(path).suffix == ".pdf":
		return False
	pipeServer = namedPipe.Server(constants.PIPE_NAME)
	pipeServer.start()
	subprocess.run(("pdftotext", path, pipeServer.getFullName()))
	list = pipeServer.getNewMessageList()
	pipeServer.exit()
	text = list[0]
	if pattern.search(text) is not None:
		return True
	return False

def _pdf_convert(path, images):
	tmp = pathlib.Path(globalVars.app.tmpdir)
	if tmp.exists():
		util.allDelete(tmp)
	tmp.mkdir()
	images += convert_from_path(path, output_folder=str(tmp), thread_count=os.cpu_count()-1, fmt="png", dpi=400)

def pdf_to_image(name):
	path = pathlib.Path(name)
	if not path.suffix == ".pdf":
		return False
	images = []
	pdfThread = threading.Thread(target = _pdf_convert, args = (str(path), images), name = "pdfThread")
	pdfThread.start()
	pdfThread.join()
	return images

