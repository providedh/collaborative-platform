from lxml import etree as et


class ContentExtractor:
    namespaces = {
        'default': 'http://www.tei-c.org/ns/1.0',
        'xml': 'http://www.w3.org/XML/1998/namespace',
        'xi': 'http://www.w3.org/2001/XInclude',
    }

    @classmethod
    def tei_contents_to_text(cls, contents):
        if not contents:
            return ""
        tree = et.fromstring(contents)
        body = tree.xpath('//default:text/default:body', namespaces=cls.namespaces)[0]
        text_nodes = body.xpath('.//text()')
        plain_text = ''.join(text_nodes)
        return str(plain_text)
