#sourceBase

import threading
from logging import getLogger
import constants
import queue

class sourceBase(threading.Thread):
	def __init__(self, identifier):
		self.identifier = identifier# このソースを表す文字列
		self.error = False
		self.log=getLogger("%s.%s" % (constants.LOG_PREFIX,identifier))
		self.messageQueue = queue.Queue()
		super().__init__()

	def initialize(self):
		return

	def _internal_get_item(self):
		raise NotImplementedError()

	def get_item(self):
		self.log.info("The item was sent to manager")
		return self._internal_get_item()

	def empty(self):
		raise NotImplementedError()

	def run(self):
		return

	def getStatusString(self):
		return _("未定義")

	def _showMessage(self, text):
		result = queue.Queue()
		data = (text, result)
		self.messageQueue.put(data)
		while not result.empty():
			time.sleep(0.01)
		return result.get()

	def close(self):
		"""ソースを閉じるときの処理"""
		return None#必要な場合はオーバーライドする。

