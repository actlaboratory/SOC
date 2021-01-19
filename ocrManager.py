import errorCodes
import threading
import time

def type_to_constant(type):
	if type.lower() == ".jpg":
		return errorCodes.TYPE_JPG
	elif type.lower() == ".png":
		return errorCodes.TYPE_PNG
	elif type.lower() == ".gif":
		return errorCodes.TYPE_GIF
	elif type.lower() == ".pdf":
		return errorCodes.TYPE_PDF_ALL
	elif type.lower() == ".bmp":
		return errorCodes.TYPE_BMP
	else:
		return errorCodes.TYPE_UNKNOWN

class manager(threading.Thread):
	def __init__(self, engine, source):
		super().__init__()
		self.processedContainers = []
		self.engine = engine
		self.source = source
		self.done = False

	def run(self):
		self.source.initialize()
		self.source.start()
		while True:
			if self.source.getStatus() & errorCodes.STATUS_SOURCE_EMPTY == errorCodes.STATUS_SOURCE_EMPTY and self.source.getStatus() & errorCodes.STATUS_SOURCE_QUEUED != errorCodes.STATUS_SOURCE_QUEUED:
				break
			if self.source.getStatus() & errorCodes.STATUS_SOURCE_LOADING == errorCodes.STATUS_SOURCE_LOADING and self.source.getStatus() & errorCodes.STATUS_SOURCE_QUEUED != errorCodes.STATUS_SOURCE_QUEUED:
				time.sleep(0.1)
				continue
			file = self.source.get()
			self.engine.recognition(file)
			self.processedContainers.append(file)
			time.sleep(0.01)
		self.done = True
		return

	def getStatusString(self):
		statuses = {}
		statuses["source"] = self.source.getStatusString()
		statuses["engine"] = self.engine.getStatusString()
		return statuses

	def getText(self):
		text = ""
		for container in self.processedContainers:
			if container.getStatus() & errorCodes.STATUS_ENGINE_SUCCESS == errorCodes.STATUS_ENGINE_SUCCESS:
				text = container.getText()
		return text

	def isDone(self):
		return self.done
