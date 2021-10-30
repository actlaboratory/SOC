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
			events.job.PROCESS_COMPLETED: self.onJobProcessed,
			events.item.ADDED: self.onItemAdded,
			events.item.CONVERTED: self.onItemConverted,
			events.job.PROCESS_STARTED: self.onJobProcessStarted,
			events.job.CONVERT_STARTED: self.onJobConversionStarted,
			events.job.CONVERT_COMPLETED: self.onJobConverted,
		}
		self.counts = {}

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
		engine = task.getEngine()
		self.mainView.addJob(job, engine)
		# job
		self.mainView.jobs.append(job)
		self.mainView.jobCtrl.Append([job.getName()])
		# page
		self.mainView.pages.append([None])
		self.mainView.selectedPages.append(0)
		# text
		self.mainView.texts.append(["",])
		# cursor
		self.mainView.cursors.append([0])

	def onItemProcessed(self, task, job, item, source, engine, converter):
		index = self.mainView.getJobIdIndex(job.getID())
		self.mainView.setProcessedCount(index, self.mainView.getProcessedCount(index) + 1)
		jobIdx = self.mainView.getJobIdx(job)
		# page
		self.mainView.pages[jobIdx].append(item)
		if jobIdx == self.mainView.jobCtrl.GetFocusedItem():
			self.mainView.pageCtrl.Append([_("%dページ") % (self.mainView.pageCtrl.GetItemCount())])
			if self.mainView.pageCtrl.GetFocusedItem() < 0:
				self.mainView.pageCtrl.Focus(0)
				self.mainView.pageCtrl.Select(0)
			self.mainView.pageCtrl.Enable()
		# text
		text = item.getText()
		self.mainView.texts[jobIdx].append(text)
		self.mainView.texts[jobIdx][0] += text
		self.mainView.texts[0] += text
		# cursor
		self.mainView.cursors[jobIdx].append(0)

	def onJobProcessed(self, task, job, item, source, engine, converter):
		index = self.mainView.getJobIdIndex(job.getID())
		status = _("完了")
		self.mainView.jobStatuses[index] = status
		self.mainView.statusList.SetItem(index, 1, status)

	def onItemAdded(self, task, job, item, source, engine, converter):
		id = job.getID()
		index = self.mainView.getJobIdIndex(id)
		self.mainView.setTotalCount(index, self.mainView.getTotalCount(index) + 1)
		self.counts[id] = self.counts.get(id, 0) + 1

	def onItemConverted(self, task, job, item, source, engine, converter):
		id = job.getID()
		index = self.mainView.getJobIdIndex(id)
		tmp = self.counts[id] - 1
		if tmp < 0:
			self.mainView.setTotalCount(index, self.mainView.getTotalCount(index) + 1)
			return
		self.counts[id] = tmp

	def onJobProcessStarted(self, task, job, item, source, engine, converter):
		index = self.mainView.getJobIdIndex(job.getID())
		if self.mainView.getJobStatus(index) != _("認識待ち"):
			return
		status = _("認識中")
		self.mainView.jobStatuses[index] = status
		self.mainView.statusList.SetItem(index, 1, status)

	def onJobConversionStarted(self, task, job, item, source, engine, converter):
		index = self.mainView.getJobIdIndex(job.getID())
		if self.mainView.getJobStatus(index) != _("待機中"):
			return
		status = _("準備中")
		self.mainView.jobStatuses[index] = status
		self.mainView.statusList.SetItem(index, 1, status)

	def onJobConverted(self, task, job, item, source, engine, converter):
		index = self.mainView.getJobIdIndex(job.getID())
		if self.mainView.getJobStatus(index) != _("準備中"):
			return
		status = _("認識待ち")
		self.mainView.jobStatuses[index] = status
		self.mainView.statusList.SetItem(index, 1, status)
