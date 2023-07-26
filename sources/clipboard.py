# clipboard source

import os
import wx

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
				raise Exception("not Available")
			data = c.get_data(ClipboardFormats.dib)
		fn = os.path.join(globalVars.app.getTmpDir(), "clipboard.bmp")
		with open(fn, "wb") as f:
			f.write(data)

		job = jobObjects.job(fn, False, self, self.engine)
		self.onJobCreated(job)
		item = jobObjects.item(fn)
		job.addCreatedItem(item)
		job.endSource()
		return
