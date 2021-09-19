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
			# event: function,
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
