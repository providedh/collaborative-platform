from lxml import etree


class XMLFormatter:
    def __init__(self):
        pass

    def check_if_reformat_is_needed(self, text):
        text_in_lines = text.splitlines()

        if 'encoding=' in text_in_lines[0]:
            text_to_reformat = '\n'.join(text_in_lines[1:])
        else:
            text_to_reformat = text

        text_reformatted = self.reformat_xml(text_to_reformat)

        if text_to_reformat != text_reformatted:
            return True

    def reformat_xml(self, text):
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.fromstring(text, parser=parser)
        pretty_xml = etree.tounicode(tree, pretty_print=True)

        if 'xml version="' not in pretty_xml:
            pretty_xml = '\n'.join((u'<?xml version="1.0"?>', pretty_xml))

        return pretty_xml
