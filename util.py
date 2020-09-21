import pathlib
import threading


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

