from .corrector import AbstractCorrector
import re


class CorrectorDate(AbstractCorrector):
    def __init__(self):
        super().__init__()
        self._corrector_type = "date"

    def _get_declarations_to_switch(self, attribute_name, attribute_value):
        attribute_value_without_space = attribute_value.replace(' ', '')

        if "AM" in attribute_value or "B.C." in attribute_value or "BC" in attribute_value:
            old_declaration, new_declaration = self.get_default_declarations(attribute_name, attribute_value)

            return old_declaration, new_declaration

        # "aaa1234-1234-1234/1234-1234-1234bbb"
        elif re.match(r'"\D*?([\d]{1,4})-([\d]{1,4})-([\d]{1,4})/([\d]{1,4})-([\d]{1,4})-([\d]{1,4})\D*?"',
                      attribute_value_without_space):
            match = re.match(r'"\D*?([\d]{1,4})-([\d]{1,4})-([\d]{1,4})/([\d]{1,4})-([\d]{1,4})-([\d]{1,4})\D*?"',
                             attribute_value_without_space)

            date_1 = self.recognize_date_parts(match.group(1), match.group(2), match.group(3))
            date_2 = self.recognize_date_parts(match.group(4), match.group(5), match.group(6))

            if date_1['y'] and date_1['m'] and date_1['d'] and date_2['y'] and date_2['m'] and date_2['d']:
                old_declaration = attribute_name + '=' + attribute_value
                new_declaration = 'from="{:04d}-{:02d}-{:02d}" to="{:04d}-{:02d}-{:02d}" {}-custom={}'.format(
                    date_1['y'], date_1['m'], date_1['d'], date_2['y'], date_2['m'], date_2['d'],
                    attribute_name, attribute_value)

            else:
                old_declaration, new_declaration = self.get_default_declarations(attribute_name, attribute_value)

            return old_declaration, new_declaration

        # "aaa1234-1234-1234/1234-1234bbb"
        elif re.match(r'"\D*?([\d]{1,4})-([\d]{1,4})-([\d]{1,4})/([\d]{1,4})-([\d]{1,4})\D*?"',
                      attribute_value_without_space):
            match = re.match(r'"\D*?([\d]{1,4})-([\d]{1,4})-([\d]{1,4})/([\d]{1,4})-([\d]{1,4})\D*?"',
                             attribute_value_without_space)

            date_1 = self.recognize_date_parts(match.group(1), match.group(2), match.group(3))
            date_2 = self.recognize_date_parts(match.group(4), match.group(5))

            if date_1['y'] and date_1['m'] and date_1['d'] and date_2['m'] and date_2['d']:
                old_declaration = attribute_name + '=' + attribute_value
                new_declaration = 'from="{0:04d}-{1:02d}-{2:02d}" to="{0:04d}-{3:02d}-{4:02d}" {5}-custom={6}'.format(
                    date_1['y'], date_1['m'], date_1['d'], date_2['m'], date_2['d'], attribute_name, attribute_value)

            else:
                old_declaration, new_declaration = self.get_default_declarations(attribute_name, attribute_value)

            return old_declaration, new_declaration

        # "aaa1234-1234-1234/1234bbb"
        elif re.match(r'"\D*?([\d]{1,4})-([\d]{1,4})-([\d]{1,4})/([\d]{1,4})\D*?"',
                      attribute_value_without_space):
            match = re.match(r'"\D*?([\d]{1,4})-([\d]{1,4})-([\d]{1,4})/([\d]{1,4})\D*?"',
                             attribute_value_without_space)

            date_1 = self.recognize_date_parts(match.group(1), match.group(2), match.group(3))
            date_2 = self.recognize_date_parts(match.group(4))

            if date_1['y'] and date_1['m'] and date_1['d'] and date_2['d']:
                old_declaration = attribute_name + '=' + attribute_value
                new_declaration = 'from="{0:04d}-{1:02d}-{2:02d}" to="{0:04d}-{1:02d}-{3:02d}" {4}-custom={5}'.format(
                    date_1['y'], date_1['m'], date_1['d'], date_2['d'], attribute_name, attribute_value)

            else:
                old_declaration, new_declaration = self.get_default_declarations(attribute_name, attribute_value)

            return old_declaration, new_declaration

        # "aaa1234-1234-1234bbb"
        elif re.match(r'"\D*?([\d]{1,4})-([\d]{1,4})-([\d]{1,4})\D*?"', attribute_value_without_space):
            match = re.match(r'"\D*?([\d]{1,4})-([\d]{1,4})-([\d]{1,4})\D*?"', attribute_value_without_space)

            date = self.recognize_date_parts(match.group(1), match.group(2), match.group(3))

            if date['y'] and date['m'] and date['d']:
                old_declaration = attribute_name + '=' + attribute_value
                new_declaration = '{3}="{0:04d}-{1:02d}-{2:02d}" {3}-custom={4}'.format(
                    date['y'], date['m'], date['d'], attribute_name, attribute_value)

            else:
                old_declaration, new_declaration = self.get_default_declarations(attribute_name, attribute_value)

            return old_declaration, new_declaration

        # "aaa1234-1234bbbb"
        elif re.match(r'"\D*?([\d]{1,4})-([\d]{1,4})\D*?"', attribute_value_without_space):
            match = re.match(r'"\D*?([\d]{1,4})-([\d]{1,4})\D*?"', attribute_value_without_space)

            date = self.recognize_date_parts(match.group(1), match.group(2))

            if date['y'] and date['m']:
                old_declaration = attribute_name + '=' + attribute_value
                new_declaration = '{2}="{0:04d}-{1:02d}" {2}-custom={3}'.format(
                    date['y'], date['m'], attribute_name, attribute_value)

            else:
                old_declaration, new_declaration = self.get_default_declarations(attribute_name, attribute_value)

            return old_declaration, new_declaration

        # "aaa1234bbb"
        elif re.match(r'"\D*?([\d]{1,4})\D*?"', attribute_value_without_space):
            match = re.match(r'"\D*?([\d]{1,4})\D*?"', attribute_value_without_space)

            date = self.recognize_date_parts(match.group(1))

            if date['y']:
                old_declaration = attribute_name + '=' + attribute_value
                new_declaration = '{1}="{0:04d}" {1}-custom={2}'.format(
                    date['y'], attribute_name, attribute_value)

            else:
                old_declaration, new_declaration = self.get_default_declarations(attribute_name, attribute_value)

            return old_declaration, new_declaration

        else:
            old_declaration, new_declaration = self.get_default_declarations(attribute_name, attribute_value)

            return old_declaration, new_declaration

    def recognize_date_parts(self, *args):
        year_candidates = []
        month_candidates = []
        day_candidates = []

        for value in args:
            value = int(value)

            if value > 31:
                year_candidates.append(value)
            elif value > 12:
                day_candidates.append(value)
            else:
                month_candidates.append(value)

        date = {
            'y': False,
            'm': False,
            'd': False
        }

        if len(year_candidates) == 1:
            date['y'] = year_candidates[0]

        if len(month_candidates) == 1:
            date['m'] = month_candidates[0]

        if len(day_candidates) == 1:
            date['d'] = day_candidates[0]

        return date

    def get_default_declarations(self, attribute_name, attribute_value):
        old_declaration = attribute_name + '=' + attribute_value
        new_declaration = attribute_name + '-custom=' + attribute_value

        return old_declaration, new_declaration
