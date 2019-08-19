import re
from lxml import etree as et


class ContentExtractor:
    namespaces = {'tei': 'http://www.tei-c.org/ns/1.0'}

    @classmethod
    def tei_contents_to_text(cls, contents):
        if not contents:
            return ""
        text = et.fromstring(contents).find('tei:text', namespaces=cls.namespaces)
        if text is None:
            return ""
        text = str(et.tostring(text), 'UTF-8')
        return ' '.join(re.sub("<.*?>", "", text).split())
