import threading
import time
import queue
from logging import getLogger
import constants
from sources.constants import sourceStatus
from engines.constants import engineStatus
from task import taskStatus

class manager(threading.Thread):
	def __init__(self):
		super().__init__()
		self.taskQueue = queue.Queue()
		self.tasks = []
		self.needStop = False
		self.running = False
		self.log = getLogger("%s.manager" % (constants.APP_NAME))

	def run(self):
		self.running = True
		while self.needStop:
			time.sleep(0.01)
			task = self.taskQueue.get(True)
			self.processTask(task)
		self.running = False

	def processTask(self, task):
		task.start()
		while task.getStatus() & taskStatus.DONE:
			time.sleep(0.01)
			continue
		return

	def addTask(self, task):
		self.tasks.append(task)
		self.taskQueue.put(task)


	def stop(self):
		self.needStop = True

	def isRunning(self):
		return self.running

	def getTasks(self):
		return self.tasks

