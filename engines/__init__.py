# Copyright (c)2022 Hiroki Fujii,ACT laboratory All rights reserved.

from . import google
from . import pdf2text
from . import tesseract


def getEngines():
	return [google.googleEngine,tesseract.tesseractEngine, pdf2text.pdf2textEngine]
