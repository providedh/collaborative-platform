import re

from .custom_entities_to_entities import name2name as cee
from .custom_entities_to_char import name2codepoint as cec
from html.entities import name2codepoint as he, html5 as h5e


class EntitiesDecoder:
    def __init__(self):
        self.xml_entities = ['&quot;', '&amp;', '&apos;', '&lt;', '&gt;']

    def decode_non_xml_entities(self, text):
        text = self.__decode_html_entities(text)
        text = self.__decode_html5_entities(text)
        text = self.__decode_custom_entities_to_entities(text)
        text = self.__decode_custom_entities_to_char(text)

        return text

    def __decode_html_entities(self, text):
        for entity in re.findall('&(?:[a-zA-Z][a-z0-9]+);', text):
            if entity in self.xml_entities:
                continue

            entity = entity.replace('&', '')
            entity = entity.replace(';', '')

            try:
                text = text.replace('&%s;' % entity, chr(he[entity]))
            except KeyError:
                pass

        return text

    def __decode_html5_entities(self, text):
        for entity in re.findall('&(?:[a-zA-Z][a-z0-9]+);', text):
            if entity in self.xml_entities:
                continue

            entity = entity.replace('&', '')

            try:
                text = text.replace('&%s' % entity, h5e[entity])
            except KeyError:
                pass

        return text

    def __decode_custom_entities_to_entities(self, text):
        for entity in re.findall('&(?:[a-zA-Z][a-zA-Z0-9]+);', text):
            if entity in self.xml_entities:
                continue

            entity = entity.replace('&', '')
            entity = entity.replace(';', '')

            try:
                text = text.replace('&%s;' % entity, cee[entity])
            except KeyError:
                pass

        return text

    def __decode_custom_entities_to_char(self, text):
        for entity in re.findall('&(?:[a-zA-Z][a-zA-Z0-9]+);', text):
            if entity in self.xml_entities:
                continue

            entity = entity.replace('&', '')
            entity = entity.replace(';', '')

            try:
                text = text.replace('&%s;' % entity, chr(cec[entity]))
            except KeyError:
                raise KeyError("Missing entity \"{}\" in \"custom_entities_to_char.py\" and "
                               "\"custom_entities_to_entities.py\" dictionary. Add this entity to "
                               "\"custom_entities_to_char.py\" or \"custom_entities_to_entities.py\" dictionary".format(entity))

        return text

    def remove_non_xml_entities(self, text):
        for entity in re.findall('&(?:[a-zA-Z][a-zA-Z0-9]+);', text):
            if entity in self.xml_entities:
                continue

            entity = entity.replace('&', '')
            entity = entity.replace(';', '')

            text = text.replace('&%s;' % entity, '')

        return text
