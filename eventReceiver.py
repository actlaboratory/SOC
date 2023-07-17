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
			events.job.PROCESS_COMPLETED: self.onJobProcessed,
			events.job.STATUS_CHANGED: self.updateListCtrl,
			events.item.CONVERTED: self.updateListCtrl,
			events.item.PROCESSED: self.onItemProcessed,
		}
		self.counts = {}

	def onEvent(self, event, job=None, item=None, source=None, engine=None, converter=None):
		self.log.debug("event: %s" % event)
		if event not in self.callbacks.keys():
			self.log.debug("Unknown event: %s" % event)
			return
		func = self.callbacks[event]
		if func is None:
			self.log.debug("Skipped event: %s" % event)
		else:
			self.log.debug("Processing event: %s" % event)
			func(job, item, source, engine, converter)

	def onJobCreated(self, job, item, source, engine, converter):
		self.mainView.jobCtrl.Append(job)
		self.mainView.statusList.SetItemCount(self.mainView.jobCtrl.GetItemCount())
		self.mainView.statusList.RefreshItem(self.mainView.statusList.index(job))

	def onJobProcessed(self, job, item, source, engine, converter):
		# TODO: 通知音再生
		pass

	def updateListCtrl(self, job, item, source, engine, converter):
		self.mainView.jobCtrl.RefreshItem(self.mainView.jobCtrl.index(job))
		self.mainView.statusList.RefreshItem(self.mainView.statusList.index(job))

	def onItemProcessed(self, job, item, source, engine, converter):
		# ジョブ一覧とステータス一覧の認識済みページ数を更新
		self.updateListCtrl(job, item, source, engine, converter)
		# 当該ジョブを閲覧中の場合のみ
		if self.mainView.getCurrentJob() == job:
			#ページ一覧を更新
			self.mainView.pageCtrl.SetItemCount(job.getProcessedCount() + 1)
			# 最初のページの追加の場合、ページ一覧を有効化
			if job.getProcessedCount() == 1:
				self.mainView.pageCtrl.Enable()
