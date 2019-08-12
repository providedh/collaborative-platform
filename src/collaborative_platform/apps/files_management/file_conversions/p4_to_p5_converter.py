from io import StringIO
import lxml.etree as et
import os
import re

from .corrector_date import CorrectorDate
from .corrector_language import CorrectorLanguage


settings_for_dates_in_date_tags = {
    'tags_to_find_regexes': [
        '<date.*?>',
    ],
    'arguments_to_check': [
        'when', 'notBefore', 'notAfter', 'from', 'to',
        'when-iso', 'notBefore-iso', 'notAfter-iso', 'from-iso', 'to-iso',
    ],
    'correct_values_regexes': [
        r'"\d\d\d\d"',
        r'"\d\d\d\d-\d\d"',
        r'"\d\d\d\d-\d\d-\d\d"',
    ]
}

correct_language_declaration_regex = [
    r'"[a-z]{2,3}"',
    r'"[a-z]{2,3}-[a-z]{3}"',
    r'"[a-z]{2,3}-[A-Z][a-z]{3}"',
    r'"[a-z]{2,3}-[a-z]{3}-[A-Z][a-z]{3}"',
]

settings_for_languages_in_langUsage_section = {
    'tags_to_find_regexes': [
        '<language.*?>',
    ],
    'arguments_to_check': [
        'ident',
    ],
    'correct_values_regexes': correct_language_declaration_regex
}

settings_for_languages_in_all_tags = {
    'tags_to_find_regexes': [
        '<.*?>',
    ],
    'arguments_to_check': [
        'xml:lang',
    ],
    'correct_values_regexes': correct_language_declaration_regex
}


class P4ToP5Converter:
    def __init__(self):
        self.transformation_file = "p4top5.xsl"

    def convert(self, text):
        text = self.__xslm_transformation(text)
        text = self.__convert_dates(text)
        text = self.__convert_languages(text)

        return text

    def __xslm_transformation(self, text):
        dom = et.parse(StringIO(text))

        dir_name = os.path.dirname(__file__)
        xslt_path = os.path.join(dir_name, self.transformation_file)

        with open(xslt_path, 'r') as file:
            xslt_text = file.read()

        xslt = et.parse(StringIO(xslt_text))
        transform = et.XSLT(xslt)
        new_dom = transform(dom)

        text = et.tostring(new_dom, xml_declaration=True, encoding='utf-8').decode('utf-8')
        text = self.__normalize_xml_declaration_quotes(text)

        return text

    def __normalize_xml_declaration_quotes(self, text):
        text_in_lines = text.splitlines()

        first_line = text_in_lines[0]
        first_line = first_line.replace('\'', '"')

        lines_to_join = [first_line] + text_in_lines[1:]
        text = '\n'.join(lines_to_join)

        return text

    def __convert_dates(self, text):
        tags_with_wrong_dates = self.__get_tags_with_wrong_declarations(text, settings_for_dates_in_date_tags)

        if tags_with_wrong_dates:
            corrector = CorrectorDate()
            text = self.__correct_tags_with_wrong_declarations(text, tags_with_wrong_dates, corrector)

        return text

    def __convert_languages(self, text):
        settings_set = [settings_for_languages_in_langUsage_section,
                        settings_for_languages_in_all_tags]

        for settings in settings_set:
            tags_with_wrong_languages = self.__get_tags_with_wrong_declarations(text, settings)

            if tags_with_wrong_languages:
                corrector = CorrectorLanguage()
                text = self.__correct_tags_with_wrong_declarations(text, tags_with_wrong_languages, corrector)

        return text

    def __get_tags_with_wrong_declarations(self, text, settings):
        tags_to_find_regexes = settings['tags_to_find_regexes']
        tags_to_check = self.__get_tags_to_check(text, tags_to_find_regexes)

        arguments_to_check = settings['arguments_to_check']
        correct_values_regexes = settings['correct_values_regexes']
        tags_with_wrong_declarations = self.__filter_tags_with_wrong_declarations(tags_to_check, arguments_to_check,
                                                                                  correct_values_regexes)

        return tags_with_wrong_declarations

    def __get_tags_to_check(self, text, tags_regex_list):
        tags = []

        for regex in tags_regex_list:
            tags = re.findall(regex, text)

        tags = set(tags)

        return tags

    def __filter_tags_with_wrong_declarations(self, tags_to_check, arguments_list, correct_values_regexes):
        tags_with_wrong_declarations = {}

        for tag in tags_to_check:
            wrong_declarations = []

            for argument in arguments_list:
                argument_declaration = argument + '="'

                if argument_declaration in tag:
                    argument_declaration_regex = r'' + argument + '=".*?"'
                    match = re.search(argument_declaration_regex, tag)
                    argument_declaration = match.group()

                    argument_value = argument_declaration.replace(argument, '')
                    argument_value = argument_value.replace('=', '')

                    found = 0

                    for regex in correct_values_regexes:
                        if re.match(regex, argument_value):
                            found += 1

                    if not found:
                        wrong_declaration = {'argument': argument, 'wrong_value': argument_value}

                        if wrong_declaration not in wrong_declarations:
                            wrong_declarations.append(wrong_declaration)

            if len(wrong_declarations) > 0:
                tags_with_wrong_declarations.update({tag: wrong_declarations})

        return tags_with_wrong_declarations

    def __correct_tags_with_wrong_declarations(self, text, tags_with_wrong_declarations, corrector):
        for tag in tags_with_wrong_declarations:
            tag_text = tag
            wrong_declarations = tags_with_wrong_declarations[tag]

            new_tag_text = corrector.get_corrected_tag(tag_text, wrong_declarations)

            text = text.replace(tag_text, new_tag_text)

        return text
