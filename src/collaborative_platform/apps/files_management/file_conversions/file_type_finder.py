import csv
import logging

from io import BytesIO
from lxml import etree

from .recognized_types import FileType

logger = logging.getLogger(__name__)


class FileTypeFinder:
    def __init__(self):
        pass

    def check_if_xml(self, text_binary):
        try:
            etree.parse(BytesIO(text_binary))

            return FileType.XML

        except etree.XMLSyntaxError as err:
            logger.info("checking if xml: {}".format(err))

            return FileType.OTHER

    def check_if_csv_or_tsv(self, text):
        fragment_to_check = text[:1024]

        try:
            file_has_header = csv.Sniffer().has_header(fragment_to_check)
            dialect = csv.Sniffer().sniff(fragment_to_check)
            delimiter = dialect.delimiter

            if file_has_header and delimiter == ',':
                return FileType.CSV

            elif file_has_header and delimiter == '\t':
                return FileType.TSV

        except Exception as ex:
            logger.info("checking if csv or tsv: {}".format(ex))

            return FileType.OTHER
