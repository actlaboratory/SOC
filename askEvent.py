# ask event

import wx

import queue

class askEventBase:
	_message = ""
	_selection_to_result = {}
	_title = ""

	def __init__(self):
		self._result_queue = queue.Queue()

	def getMessage(self):
		return self._message

	def getSelectionCount(self):
		return len(self._selection_to_result)

	def getSelections(self):
		return self._selection_to_result

	def getTitle(self):
		return self._title

	def getResult(self, wait = True):
		return self._result_queue.get(wait)

	def setResult(self, result):
		self._result_queue.put(result)

class notice(askEventBase):
	def __init__(self, title, message):
		self._title = title
		self._message = message
		self._selection_to_result = {
			_("OK"): wx.ID_OK,
		}
		super().__init__()
