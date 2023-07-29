# clipboard source

import os

import askEvent
import globalVars
import jobObjects

from clipboardHelper import *

from .base import sourceBase, sourceAskEvent

class ClipboardSource(sourceBase):
	def __init__(self):
		super().__init__("clipboardSource")


	def _run(self):
		with Clipboard() as c:
			if not c.is_format_available(ClipboardFormats.dib):
				self.ask(askEvent.notice(_("クリップボードから読込"), _("クリップボードに画像が保存されていません。")))
				return
			data = c.get_data(ClipboardFormats.dib)
		fn = os.path.join(globalVars.app.getTmpDir(), "clipboard.bmp")
		with open(fn, "wb") as f:
			f.write(data)

		job = jobObjects.job(fn, True, self, self.engine)
		self.onJobCreated(job)
		job.addCreatedItem(jobObjects.item(fn))
		job.endSource()
