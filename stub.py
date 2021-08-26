from jobObjects import job, item


class stub:
	def __init__(self):
		self.jobs = []
		dummy = job("c:\\test\\tmp_1.png")
		dummyItem = item("c:\\test\\tmp_1.png")
		dummyItem.setText("こんにちは。\nさようなら。")
		dummy.appendItem(dummyItem)
		self.jobs.append(dummy)
		dummy = job("c:\\test\\tmp_2.jpg")
		dummyItem = item("c:\\test\\tmp_2.jpg")
		dummyItem.setText("この度はこのようなソフトをご利用いただきまして誠にありがとうございます。\nこのソフトは正式版ではありますが、大変仕様の多いソフトとなっております。\nバグと思われた際は、当ラボに報告するのではなく、仕様とお考え下さい。")
		dummy.appendItem(dummyItem)
		self.jobs.append(dummy)
		dummy = job("c:\\test\\tmp_3.pdf")
		dummyItem = item("c:\\tmp\\test1.png")
		dummyItem.setText("これはPDFの１ページでございます。ページを分割してページごとに認識することがあります。")
		dummy.appendItem(dummyItem)
		dummyItem = item("c:\\tmp\\test_2.png")
		dummyItem.setText("２ページ目でございます。\nスタブ作るのも結構大変です。")
		dummy.appendItem(dummyItem)
		self.jobs.append(dummy)
		self.processedJobs = []

	def getEngineStatus(self):
		return 0

	def getSourceStatus(self):
		return 0

	def getProcessedJobs(self):
		return self.processedJobs

	def getAllText(self):
		jobs = self.getProcessedJobs()
		text = ""
		for i in jobs:
			text += i.getAllItemText()
		return text

	def processNextJob(self):
		self.processedJobs.append(self.jobs[0])
		del self.jobs[0]
