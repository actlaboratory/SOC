# ask event

import queue

class askEventBase:
	_message = ""
	_selection_to_result = {}
	_title = ""

	def __init__(self, obj):
		self.eventObject = obj
		self._result_queue = queue.Queue()

	def getEventObject(self):
		return self.eventObject

	def getMessage(self):
		return self._message

	def getSelections(self):
		return self._selection_to_result

	def setResult(self, result):
		self._result_queue.put(result)

	def getResult(self, wait = True):
		result = self._result_queue.get(wait)
		return result

	def getTitle(self):
		return self._title
