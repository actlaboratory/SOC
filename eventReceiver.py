# Event Receiver

import logging

import constants
import events
import globalVars
import views.main

class EventReceiver:
	def __init__(self, mainView):
		self.mainView: views.main.MainView = mainView
		self.log = logging.getLogger("%s.%s" % (constants.LOG_PREFIX, "eventReceiver"))
		self.callbacks = {
			events.job.CREATED: self.onJobCreated,
			events.item.PROCESSED: self.onItemProcessed,
			events.job.PROCESS_COMPLETED: self.onJobProcessed,
			events.job.STATUS_CHANGED: self.updateListCtrl,
			events.item.ADDED: self.onItemAdded,
		}
		self.counts = {}

	def onEvent(self, event, task, job=None, item=None, source=None, engine=None, converter=None):
		self.log.debug("event: %s" % event)
		if event not in self.callbacks.keys():
			self.log.debug("Unknown event: %s" % event)
			return
		func = self.callbacks[event]
		if func is None:
			self.log.debug("Skipped event: %s" % event)
		else:
			self.log.debug("Processing event: %s" % event)
			func(task, job, item, source, engine, converter)

	def onJobCreated(self, task, job, item, source, engine, converter):
		globalVars.app.hMainView.jobCtrl.Append(job)
		globalVars.app.hMainView.statusList.SetItemCount(globalVars.app.hMainView.jobCtrl.GetItemCount())
		globalVars.app.hMainView.statusList.RefreshItem(globalVars.app.hMainView.statusList.index(job))

		# page
		self.mainView.pages.append([None])
		self.mainView.selectedPages.append(0)
		# text
		self.mainView.texts.append(["",])
		# cursor
		self.mainView.cursors.append([0])

	def updateListCtrl(self, task, job, item, source, engine, converter):
		globalVars.app.hMainView.jobCtrl.RefreshItem(globalVars.app.hMainView.jobCtrl.index(job))
		globalVars.app.hMainView.statusList.RefreshItem(globalVars.app.hMainView.statusList.index(job))
		# すべて の中も更新
		globalVars.app.hMainView.jobCtrl.RefreshItem(0
		globalVars.app.hMainView.statusList.RefreshItem(0)

	def onItemProcessed(self, task, job, item, source, engine, converter):
		self.updateListCtrl(task, job, item, source, engine, converter)
		jobIdx = globalVars.app.hMainView.jobCtrl.index(job)

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
		# TODO: 通知音再生
		pass

	def onItemAdded(self, task, job, item, source, engine, converter):
		self.updateListCtrl(task, job, item, source, engine, converter)
