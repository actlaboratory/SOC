import pathlib
import threading
import os
import uuid
import globalVars

def allDelete(dirname):
	"""dirnameに指定したディレクトリの中身をすべて削除する。
	dirname: 削除するディレクトリ。pathlibオブジェクトまたはパスの文字列で指定できる。
	"""
	if isinstance(dirname, pathlib.WindowsPath):
		path = dirname
	else:
		path = pathlib.Path(dirname)
	for tmp in path.iterdir():
		if tmp.is_dir():
			allDelete(tmp)
		if tmp.is_file():
			tmp.unlink()
	path.rmdir()
	return


def textSave(name, text):
	if isinstance(name, pathlib.WindowsPath):
		path = name
	else:
		path = pathlib.Path(name)
	path.write_text(text)

def get_change_ext(filepath, new_ext):
	return "%s.%s" % (os.path.splitext(filepath)[0], new_ext)


def getTmpFilePath(ext):
	basePath = os.path.join(globalVars.app.getTmpDir(), str(uuid.uuid4()))
	return basePath+ext

