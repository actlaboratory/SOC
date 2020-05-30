"""
Builders: Each builder specifies the expected output format

raw text : TextBuilder
"""

from html.parser import HTMLParser
import logging
import xml.dom.minidom

logger = logging.getLogger(__name__)

__all__ = [
    'Box',
    'TextBuilder',
    'WordBoxBuilder',
]

_XHTML_HEADER = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
 "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
\t<meta http-equiv="content-type" content="text/html; charset=utf-8" />
\t<title>OCR output</title>
</head>
"""


class Box(object):
    """
    Boxes are rectangles around each individual element recognized in the
    image. Elements are either char or word depending of the builder that
    was used.
    """

    def __init__(self, content, position, confidence=0):
        """
        Arguments:
            content --- a single string
            position --- the position of the box on the image. Given as a
                tuple of tuple:
                ((box_pt_min_x, box_pt_min_y), (box_pt_max_x, box_pt_max_y))
        """
        self.content = content
        self.position = position
        self.confidence = confidence

    def get_xml_tag(self, parent_doc):
        span_tag = parent_doc.createElement("span")
        span_tag.setAttribute("class", "ocrx_word")
        span_tag.setAttribute("title", ("bbox %d %d %d %d; x_wconf %d" % (
            (self.position[0][0], self.position[0][1],
             self.position[1][0], self.position[1][1],
             self.confidence))))
        txt = xml.dom.minidom.Text()
        txt.data = self.content
        span_tag.appendChild(txt)
        return span_tag

    def __str__(self):
        return "{} {} {} {} {}".format(
            self.content,
            self.position[0][0],
            self.position[0][1],
            self.position[1][0],
            self.position[1][1],
        )

    def __box_cmp(self, other):
        """
        Comparison function.
        """
        if other is None or getattr(other, "position", None) is None:
            return -1
        for (x, y) in ((self.position[0][1], other.position[0][1]),
                       (self.position[1][1], other.position[1][1]),
                       (self.position[0][0], other.position[0][0]),
                       (self.position[1][0], other.position[1][0])):
            if x < y:
                return -1
            elif x > y:
                return 1
        return 0

    def __lt__(self, other):
        return self.__box_cmp(other) < 0

    def __gt__(self, other):
        return self.__box_cmp(other) > 0

    def __eq__(self, other):
        return self.__box_cmp(other) == 0

    def __le__(self, other):
        return self.__box_cmp(other) <= 0

    def __ge__(self, other):
        return self.__box_cmp(other) >= 0

    def __ne__(self, other):
        return self.__box_cmp(other) != 0

    def __hash__(self):
        position_hash = 0
        position_hash += ((self.position[0][0] & 0xFF) << 0)
        position_hash += ((self.position[0][1] & 0xFF) << 8)
        position_hash += ((self.position[1][0] & 0xFF) << 16)
        position_hash += ((self.position[1][1] & 0xFF) << 24)
        return (position_hash ^ hash(self.content) ^ hash(self.content))



class BaseBuilder(object):
    """
    Builders format the output of the OCR tools,
    and potentially configures the tools.

    Attributes:
        file_extensions : File extensions of the output.
        tesseract_configs : Arguments passed to the Tesseract command line.
    """

    def __init__(self, file_extensions, tesseract_flags, tesseract_configs,
                 cuneiform_args):
        self.file_extensions = file_extensions
        self.tesseract_flags = tesseract_flags
        self.tesseract_configs = tesseract_configs

    # used with Tesseract and Cuneiform
    def read_file(self, file_descriptor):  # pragma: no cover
        """
        Read in the OCR results from `file_descriptor`
        as an appropriate format.
        """
        raise NotImplementedError("Implement in subclasses")

    def write_file(self, file_descriptor, output):  # pragma: no cover
        """
        Write the `output` to `file_descriptor`.
        """
        raise NotImplementedError("Implement in subclasses")

    # used with Libtesseract
    def start_line(self, box):  # pragma: no cover
        """
        Start a new line of output.
        """
        raise NotImplementedError("Implement in subclasses")

    def add_word(self, word, box, confidence=0):  # pragma: no cover
        """
        Add a word to output.
        """
        raise NotImplementedError("Implement in subclasses")

    def end_line(self):  # pragma: no cover
        """
        End a line in output.
        """
        raise NotImplementedError("Implement in subclasses")

    def get_output(self):  # pragma: no cover
        """
        Return the output that has been built so far.
        """
        raise NotImplementedError("Implement in subclasses")


class TextBuilder(BaseBuilder):
    """
    If passed to image_to_string(), image_to_string() will return a simple
    string. This string will be the output of the OCR tool, as-is. In other
    words, the raw text as produced by the tool.

    Warning:
        The returned string is encoded in UTF-8
    """

    def __init__(self, tesseract_layout=3, cuneiform_dotmatrix=False,
                 cuneiform_fax=False, cuneiform_singlecolumn=False):
        from .tesseract import psm_parameter
        tess_flags = [psm_parameter(), str(tesseract_layout)]
        file_ext = ["txt"]
        cun_args = ["-f", "text"]
        # Add custom cuneiform parameters if needed
        super(TextBuilder, self).__init__(file_ext, tess_flags, [], cun_args)
        self.tesseract_layout = tesseract_layout
        self.built_text = []

    @staticmethod
    def read_file(file_descriptor):
        """
        Read a file and extract the content as a string.
        """
        return file_descriptor.read().strip()

    @staticmethod
    def write_file(file_descriptor, text):
        """
        Write a string in a file.
        """
        file_descriptor.write(text)

    def start_line(self, box):
        self.built_text.append(u"")

    def add_word(self, word, box, confidence=0):
        if self.built_text[-1] != u"":
            self.built_text[-1] += u" "
        self.built_text[-1] += word

    def end_line(self):
        pass

    def get_output(self):
        return u"\n".join(self.built_text)

    def __str__(self):
        return "Raw text"


