import errorCodes
import threading

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
		while True:
			file = self.source.get()
			self.engine.recognition(file)
			self.processedContainers.append(file)
			if self.source.isEmpty():
				break
		self.done = True
		return

	def getStatusString(self):
		return "test"

	def getText(self):
		text = ""
		for container in self.processedContainers:
			if container.getStatus() == errorCodes.STATUS_SUCCESS:
				text = container.getText()
		return text

	def isDone(self):
		return self.done
