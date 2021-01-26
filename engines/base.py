import queue
import time

class engineBase(object):
	"""すべてのエンジンクラスが継承する基本クラス。"""
	def __init__(self):
		self.interrupt = False
		self.processingContainer = []
		self.messageQueue = queue.Queue()

	def recognition(self, container):
		raise NotImplementedError()

	def getSupportedType(self):
		raise NotImplementedError()

	def setInterrupt(self):
		self.interrupt = True

	def showMessage(self, text):
		result = queue.Queue()
		data = (text, result)
		self.messageQueue.put(data)
		while not result.empty():
			time.sleep(0.01)
		return result.get()

	def getStatusString(self):
		return _("未定義")

