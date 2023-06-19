# Copyright (c)2022 Hiroki Fujii,ACT laboratory All rights reserved.

from . import google
from . import tesseract



def getEngines():
	return [google.googleEngine,tesseract.tesseractEngine]
