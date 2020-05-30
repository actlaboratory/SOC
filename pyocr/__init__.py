# NOTE: This file must remain Python 2 compatible for the foreseeable future,
# to ensure that we error out properly for existing editable installs.

from .pyocr import *  # noqa
from .error import PyocrException

__all__ = [
    'get_available_tools',
    'PyocrException',
    'TOOLS',
    'VERSION',
]
