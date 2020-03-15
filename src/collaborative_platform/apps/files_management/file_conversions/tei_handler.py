import io
import re
import logging

from bs4 import UnicodeDammit

from .migrator_tei import MigratorTEI
from .migrator_csv import MigratorCSV
from .migrator_tsv import MigratorTSV
from .migrator_plain_text import MigratorPlainText
from .xml_type_finder import XMLTypeFinder
from .file_type_finder import FileTypeFinder
from .entities_decoder import EntitiesDecoder
from .recognized_types import FileType, XMLType
from .white_chars_corrector import WhiteCharsCorrector
from .xml_formatter import XMLFormatter

logger = logging.getLogger(__name__)


class TeiHandler:
    """Stream-like handler that recognizes TEI/CSV files and migrate them to TEI P5."""

    def __init__(self):
        self.__encoding = None
        self.text = ''

        self.__text_binary = None
        self.__text_utf_8 = ''

        self.__file_type = FileType.PLAIN_TEXT
        self.__xml_type = XMLType.OTHER
        self.__prefixed = False

        self.__cr_lf_codes = False
        self.__non_unix_newline_chars = False
        self.__need_reformat = False
        self.__tei_providedh_schema_missing = False

        self.__recognized = False
        self.__migrated = False
        self.__migrate = False
        self.__message = ''

        self.__is_tei_p5_unprefixed = False

    def recognize(self, text_binary):
        self.__text_binary = text_binary

        if self.__is_default_encoded_xml(self.__text_binary):
            self.__encoding = 'utf-8'
            self.__text_utf_8 = self.__text_binary.decode(self.__encoding)

        else:
            try:
                recognize_results = UnicodeDammit(self.__text_binary)
                self.__encoding = recognize_results.original_encoding

                if not self.__encoding:
                    raise Exception("Text encoding not recognized.")

                self.__text_utf_8 = recognize_results.unicode_markup

            except Exception as ex:
                logger.info("Text encoding searching: {}".format(ex))

                return self.__migrate, self.__is_tei_p5_unprefixed

        entities_decoder = EntitiesDecoder()
        text_utf_8_without_entities = entities_decoder.remove_non_xml_entities(self.__text_utf_8)
        text_binary_without_entities = text_utf_8_without_entities.encode(self.__encoding)

        file_type_finder = FileTypeFinder()
        self.__file_type = file_type_finder.check_if_xml(text_binary_without_entities)

        if self.__file_type == FileType.PLAIN_TEXT:
            self.__file_type = file_type_finder.check_if_csv_or_tsv(self.__text_utf_8)

        if self.__file_type == FileType.XML:
            self.__text_utf_8 = entities_decoder.decode_non_xml_entities(self.__text_utf_8)
            self.__text_utf_8 = self.__remove_encoding_declaration(self.__text_utf_8)

            xml_type_finder = XMLTypeFinder()
            self.__xml_type, self.__prefixed = xml_type_finder.find_xml_type(self.__text_utf_8)

        file_types_to_correction = [FileType.XML, FileType.CSV, FileType.TSV, FileType.PLAIN_TEXT]

        if self.__file_type in file_types_to_correction:
            white_chars_corrector = WhiteCharsCorrector()
            self.__cr_lf_codes = white_chars_corrector.check_if_cr_lf_codes(self.__text_utf_8)
            self.__non_unix_newline_chars = white_chars_corrector.check_if_non_unix_newlines(self.__text_utf_8)

        if self.__file_type == FileType.XML:
            xml_formatter = XMLFormatter()
            self.__need_reformat = xml_formatter.check_if_reformat_is_needed(self.__text_utf_8)
            self.__tei_providedh_schema_missing = xml_formatter.check_if_tei_providedh_schema_missing(self.__text_utf_8)

        self.__migrate = self.__make_decision()
        self.__is_tei_p5_unprefixed = self.__check_if_tei_p5_unprefixed()
        self.__recognized = True

        return self.__migrate, self.__is_tei_p5_unprefixed

    def __is_default_encoded_xml(self, text):
        if text:
            first_line = text.splitlines()[0]
        else:
            return False

        if b'xml version=' in first_line and b'encoding=' not in first_line:
            return True
        else:
            return False

    def __remove_encoding_declaration(self, text):
        first_line = text.splitlines()[0]

        regex = r'encoding=".*?"'
        match = re.search(regex, first_line)

        if match:
            encoding_declaration = match.group()

            text = text.replace(" " + encoding_declaration, '')
            text = text.replace(" ?>", "?>")

        return text

    def __make_decision(self):
        if (self.__file_type == FileType.XML and self.__xml_type == XMLType.TEI_P5 and
                self.__encoding != 'utf-8'):
            return True
        elif self.__file_type == FileType.XML and self.__xml_type == XMLType.TEI_P5 and self.__prefixed:
            return True
        elif self.__file_type == FileType.XML and self.__xml_type == XMLType.TEI_P4:
            return True
        elif self.__file_type == FileType.CSV:
            return True
        elif self.__file_type == FileType.TSV:
            return True
        elif self.__file_type == FileType.PLAIN_TEXT:
            return True
        elif self.__cr_lf_codes:
            return True
        elif self.__non_unix_newline_chars:
            return True
        elif self.__need_reformat:
            return True
        elif self.__tei_providedh_schema_missing:
            return True
        else:
            return False

    def __check_if_tei_p5_unprefixed(self):
        if self.__file_type == FileType.XML and self.__xml_type == XMLType.TEI_P5 and not self.__prefixed:
            return True
        else:
            return False

    def migrate(self):
        if not self.__recognized:
            raise Exception("File recognition needed. Use \"recognize()\" method first.")

        elif not self.__migrate:
            raise Exception("No migration needed.")

        migrated_text = self.__text_utf_8

        if self.__file_type == FileType.XML:
            migrator_tei = MigratorTEI()
            migrated_text = migrator_tei.migrate(migrated_text, self.__xml_type)

        elif self.__file_type == FileType.CSV:
            migrator_csv = MigratorCSV()
            migrated_text = migrator_csv.migrate(migrated_text)

        elif self.__file_type == FileType.TSV:
            migrator_tsv = MigratorTSV()
            migrated_text = migrator_tsv.migrate(migrated_text)

        elif self.__file_type == FileType.PLAIN_TEXT:
            migrator_plain_text = MigratorPlainText()
            migrated_text = migrator_plain_text.migrate(migrated_text)

        if self.__cr_lf_codes:
            white_chars_corrector = WhiteCharsCorrector()
            migrated_text = white_chars_corrector.replace_cr_lf_codes(migrated_text)

        if self.__non_unix_newline_chars:
            white_chars_corrector = WhiteCharsCorrector()
            migrated_text = white_chars_corrector.normalize_newlines(migrated_text)

        migrated_text = self.__remove_encoding_declaration(migrated_text)

        xml_formatter = XMLFormatter()

        if self.__tei_providedh_schema_missing:
            migrated_text = xml_formatter.append_missing_tei_providedh_schema(migrated_text)

        if self.__need_reformat:
            migrated_text = xml_formatter.reformat_xml(migrated_text)

        self.text = migrated_text
        self.__prepare_message()
        self.__migrated = True

    def __prepare_message(self):
        prefixed = "prefixed " if self.__prefixed else ""

        file_type = {
            FileType.XML: "XML ",
            FileType.CSV: "CSV ",
            FileType.TSV: "TSV ",
            FileType.PLAIN_TEXT: "plain text ",
        }

        xml_type = {
            XMLType.TEI_P4: "TEI P4 ",
            XMLType.TEI_P5: "TEI P5 ",
            XMLType.OTHER: "",
        }

        message = ""

        if self.__file_type == FileType.XML and self.__xml_type == XMLType.TEI_P5 and not self.__prefixed:
            pass
        else:
            message += "Migrated file format from {0}{1}{2}to unprefixed TEI P5 XML.".format(prefixed,
                                                                                             xml_type[self.__xml_type],
                                                                                             file_type[self.__file_type])

        if self.__encoding != "utf-8":
            if message:
                message += " "

            message += "Changed file encoding from {0} to UTF-8.".format(self.__encoding)

        if self.__cr_lf_codes:
            if message:
                message += " "

            message += "Changed CR/LF character codes to <lb/> tags."

        if self.__non_unix_newline_chars:
            if message:
                message += " "

            message += "Normalized new line characters."

        if self.__tei_providedh_schema_missing:
            if message:
                message += " "

            message += "Appended TEI ProvideDH schema."

        if self.__need_reformat:
            if message:
                message += " "

            message += "Reformatted xml."

        self.__message = message

    def get_message(self):
        return self.__message

    def get_text(self):
        return self.text or self.__text_utf_8

    def is_migrated(self):
        return self.__migrated
