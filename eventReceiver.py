# Event Receiver

import logging

import constants
import events
import views.main

class EventReceiver:
	def __init__(self, mainView):
		self.mainView: views.main.MainView = mainView
		self.log = logging.getLogger("%s.%s" % (constants.LOG_PREFIX, "eventReceiver"))
		self.callbacks = {
			events.job.CREATED: self.onJobCreated,
			events.item.PROCESSED: self.onItemProcessed,
		}

	def onEvent(self, event, task, job=None, item=None, source=None, engine=None, converter=None):
		self.log.debug("event: %s" % event)
		if event not in self.callbacks.keys():
			self.log.warning("Unknown event: %s" % event)
			return
		func = self.callbacks[event]
		if func is None:
			self.log.debug("Skipped event: %s" % event)
		else:
			self.log.debug("Processing event: %s" % event)
			func(task, job, item, source, engine, converter)

	def onJobCreated(self, task, job, item, source, engine, converter):
		# job
		self.mainView.jobs.append(job)
		self.mainView.jobCtrl.Append([job.getName()])
		# page
		self.mainView.pages.append([])
		self.mainView.selectedPages.append(-1)
		# text
		self.mainView.texts.append(["",])
		# cursor
		self.mainView.cursors.append([0])

	def onItemProcessed(self, task, job, item, source, engine, converter):
		jobIdx = self.mainView.getJobIdx(job)
		# page
		self.mainView.pages[jobIdx].append(item)
		if jobIdx == self.mainView.jobCtrl.GetFocusedItem():
			self.mainView.pageCtrl.Enable()
			self.mainView.pageCtrl.Append(_("%dページ") % (self.mainView.pageCtrl.GetCount()))
		# text
		text = item.getText()
		self.mainView.texts[jobIdx].append(text)
		self.mainView.texts[jobIdx][0] += text
		self.mainView.texts[0] += text
		# cursor
		self.mainView.cursors[jobIdx].append(0)