import io
import csv

from xml.sax.saxutils import escape


class MigratorDSV:
    def __init__(self):
        self._delimiter = ''

    def migrate(self, text):
        text_in_xml = io.StringIO()

        tei_p5_beginning = self.__create_tei_p5_begining()
        text_in_xml.write(tei_p5_beginning)

        text_escaped = self.__escape_xml_entities(text)
        text_converted = self.__convert_dsv_to_tei_p5_table(text_escaped)
        text_in_xml.write(text_converted)

        tei_p5_end = self.__create_tei_p5_end()
        text_in_xml.write(tei_p5_end)

        text_after_migration = text_in_xml.getvalue()

        return text_after_migration

    def __escape_xml_entities(self, text):
        text_escaped = escape(text)

        return text_escaped

    def __create_tei_p5_begining(self):
        tei_p5_begining = (
            '<?xml version="1.0"?>' + '\n' +
            '<TEI xmlns="http://www.tei-c.org/ns/1.0">' + '\n' +
            '    <teiHeader>' + '\n' +
            '    </teiHeader>' + '\n' +
            '    <text>' + '\n'
        )

        return tei_p5_begining

    def __convert_dsv_to_tei_p5_table(self, text_in_dsv):
        text_in_lines = text_in_dsv.splitlines()
        dsv_data = csv.reader(text_in_lines, delimiter=self._delimiter)

        tei_p5_table = io.StringIO()

        tab = [
            '',
            '    ',
            '        ',
            '            ',
            '                ',
        ]

        rows_nr = len(text_in_lines) - 1
        cols_nr = len(text_in_lines[0].split(self._delimiter))

        tei_p5_table.write(tab[2] + '<table rows="' + str(rows_nr) + '" cols="' + str(cols_nr) + '">' + '\n')

        for i, row in enumerate(dsv_data):
            if i == 0:
                tei_p5_table.write(tab[3] + '<row role="label">' + '\n')

            else:
                tei_p5_table.write(tab[3] + '<row>' + '\n')

            for cell in row:
                tei_p5_table.write(tab[4] + '<cell>' + cell + '</cell>' + '\n')

            tei_p5_table.write(tab[3] + '</row>' + '\n')

        tei_p5_table.write(tab[2] + '</table>' + '\n')

        return tei_p5_table.getvalue()

    def __create_tei_p5_end(self):
        tei_p5_end = (
            '    </text>' + '\n' +
            '</TEI>'
        )

        return tei_p5_end
