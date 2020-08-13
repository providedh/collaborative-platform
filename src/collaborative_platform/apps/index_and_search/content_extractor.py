from lxml import etree as et

from django.conf import settings


class ContentExtractor:
    namespaces = settings.XML_NAMESPACES

    @classmethod
    def tei_contents_to_text(cls, contents: str):
        if not contents:
            return ""
        tree = et.fromstring(contents.encode("utf-8"))
        body = tree.xpath('//default:text/default:body', namespaces=cls.namespaces)[0]
        text_nodes = body.xpath('.//text()')
        text_nodes = (node.strip() for node in text_nodes if node.strip())
        plain_text = '\n'.join(text_nodes)
        return str(plain_text)
