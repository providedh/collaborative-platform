from .xml_attributes_finder import XMLAttributesFinder
from .recognized_types import XMLType


class XMLTypeFinder:
    def __init__(self):
        pass

    def find_xml_type(self, text):
        xml_attribute_detector = XMLAttributesFinder()
        root_tag, prefix, tei_p5_ns_schema = xml_attribute_detector.find_xml_attributes(text)

        if root_tag == "TEI" and tei_p5_ns_schema:
            xml_type = XMLType.TEI_P5
        elif root_tag == "TEI.2":
            xml_type = XMLType.TEI_P4
        else:
            xml_type = XMLType.OTHER

        prefixed = bool(prefix)

        return xml_type, prefixed
