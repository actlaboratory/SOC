# file source

import os

import askEvent
import jobObjects

from .base import sourceBase


class fileSource(sourceBase):
	def __init__(self, fileList):
		super().__init__("fileSource")
		self.fileList = fileList
		self.log.info("%d files was stored" % len(fileList))

	def _run(self):
		errors = []
		for file in self.fileList:
			# 実在確認しておく
			if not os.path.isfile(file):
				errors.append(file)
				self.log.error("file not found:"+file)
				continue
			job = jobObjects.job(file, False, self, self.engine)
			self.onJobCreated(job)
			job.addCreatedItem(jobObjects.item(file))
			job.endSource()
		if errors:
			self.ask(askEvent.notice(_("ファイルから読込"), _("下記のファイルは存在しないため、スキップしました。\n\n") + ("\n".join(errors))))
		return
