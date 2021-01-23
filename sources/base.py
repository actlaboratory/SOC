#sourceBase

import threading
from logging import getLogger
import constants
import queue

class sourceBase(threading.Thread):
	def __init__(self):
		self.error = False
		self.log=getLogger("%s.%s" % (constants.LOG_PREFIX,"source"))
		self.messageQueue = queue.Queue()
		super().__init__()

	def initialize(self):
		return

	def get(self):
		raise NotImplementedError()

	def isEmpty(self):
		raise NotImplementedError()

	def run(self):
		return

	def getStatusString(self):
		return _("未定義")

	def showMessage(self, text):
		result = queue.Queue()
		data = (text, result)
		self.messageQueue.put(data)
		while not result.empty():
			time.sleep(0.01)
		return result.get()

	def close(self):
		"""ソースを閉じるときの処理"""
		return None#必要な場合はオーバーライドする。

