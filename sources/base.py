#sourceBase

import threading
from logging import getLogger
import constants

class sourceBase(threading.Thread):
	def __init__(self):
		self.error = False
		self.log=getLogger("%s.%s" % (constants.LOG_PREFIX,"source"))
		super().__init__()

	def initialize(self):
		return

	def get(self):
		raise NotImplementedError()

	def isEmpty(self):
		raise NotImplementedError()

	def run(self):
		return

	def close(self):
		"""ソースを閉じるときの処理"""
		return None#必要な場合はオーバーライドする。

