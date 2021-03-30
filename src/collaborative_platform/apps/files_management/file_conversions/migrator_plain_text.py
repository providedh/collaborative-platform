import re


class MigratorPlainText:
    def __init__(self):
        pass

    def migrate(self, text):  # type: (str) -> str
        tei_beginning = self.__create_tei_p5_beginning()
        tei_body = self.__convert_plain_text_to_tei_body(text)
        tei_end = self.__create_tei_p5_end()

        tei_file = tei_beginning + tei_body + tei_end

        return tei_file

    @staticmethod
    def __create_tei_p5_beginning():  # type: () -> str
        tei_p5_beginning = (
            '<?xml version="1.0"?>' + '\n' +
            '<TEI xmlns="http://www.tei-c.org/ns/1.0">' + '\n' +
            '  <teiHeader>' + '\n' +
            '  </teiHeader>' + '\n' +
            '  <text>' + '\n' +
            '    <body>' + '\n'
        )

        return tei_p5_beginning

    @staticmethod
    def __convert_plain_text_to_tei_body(text):  # type: (str) -> str
        paragraph_open = '<p>'
        paragraph_close = '</p>'
        new_line = '\n'

        text = paragraph_open + text + paragraph_close
        text = text.replace(new_line, paragraph_close + new_line + paragraph_open)

        empty_paragraph_regex = r'[\s]*<p>[\s]*<\/p>[\s]*'
        text = re.sub(empty_paragraph_regex, '', text)

        joined_paragraph_regex = r'<\/p>[\s]*<p>'
        text = re.sub(joined_paragraph_regex, paragraph_close + new_line + paragraph_open, text)

        return text

    @staticmethod
    def __create_tei_p5_end():  # type: () -> str
        tei_p5_end = (
            '\n' +
            '    </body>' + '\n' +
            '  </text>' + '\n' +
            '</TEI>'
        )

        return tei_p5_end
