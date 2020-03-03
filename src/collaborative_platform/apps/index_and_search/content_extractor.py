from lxml import etree as et

from django.conf import settings


class ContentExtractor:
    namespaces = settings.XML_NAMESPACES

    @classmethod
    def tei_contents_to_text(cls, contents):
        if not contents:
            return ""
        tree = et.fromstring(contents)
        body = tree.xpath('//default:text/default:body', namespaces=cls.namespaces)[0]
        text_nodes = body.xpath('.//text()')
        plain_text = ''.join(text_nodes)
        return str(plain_text)
