import csv

from io import BytesIO
from lxml import etree

from apps.files_management.file_conversions.recognized_types import FileType


class FileTypeFinder:
    def __init__(self):
        pass

    @staticmethod
    def check_if_xml(text_binary):
        try:
            etree.parse(BytesIO(text_binary))

            return FileType.XML

        except etree.XMLSyntaxError:
            return FileType.PLAIN_TEXT

    @staticmethod
    def check_if_csv_or_tsv(text):
        fragment_to_check = text[:1024]

        try:
            file_has_header = csv.Sniffer().has_header(fragment_to_check)
            dialect = csv.Sniffer().sniff(fragment_to_check)
            delimiter = dialect.delimiter

            if file_has_header and delimiter == ',':
                return FileType.CSV

            elif file_has_header and delimiter == '\t':
                return FileType.TSV

        except Exception:
            return FileType.PLAIN_TEXT
