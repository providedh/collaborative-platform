import re


class TextSplitter:
    def split_text_to_autonomic_parts(self, text):
        parts = self.split(text)
        autonomic_parts = self.join(parts)

        return autonomic_parts

    def split(self, text_fragment):
        parts = []

        text_regex = r'^[^<>]+'
        tag_regex = r'^<.*?>'

        while len(text_fragment) > 0:
            text = re.search(text_regex, text_fragment)
            tag = re.search(tag_regex, text_fragment)

            if text:
                part = text.group()

            else:
                part = tag.group()

            parts.append(part)
            text_fragment = text_fragment[len(part):]

        return parts

    def join(self, parts):
        old_length = len(parts)
        new_length = 0

        while old_length != new_length:
            old_length = len(parts)

            for i, part in enumerate(parts):
                if self.is_autonomic_part(parts[i]):
                    if i > 0 and self.is_autonomic_part(parts[i - 1]):
                        new_parts = parts[:i-1]
                        new_part = parts[i-1] + parts[i]
                        new_parts.append(new_part)

                        if i < len(parts):
                            new_parts += parts[i+1:]

                        parts = new_parts
                        break

                    elif 0 < i < (len(parts)-1) and \
                            self.is_opening_tag(parts[i - 1]) and \
                            self.is_closing_tag(parts[i + 1]):
                        new_parts = parts[:i-1]
                        new_part = parts[i-1] + parts[i] + parts[i+1]
                        new_parts.append(new_part)

                        if i+1 < len(parts):
                            new_parts += parts[i+2:]

                        parts = new_parts
                        break

            new_length = len(parts)

        return parts

    @staticmethod
    def is_autonomic_part(text):
        tag_opening_regex = r'<'
        tag_closing_1_regex = r'</'
        tag_closing_2_regex = r'/>'

        tag_openings = re.findall(tag_opening_regex, text)
        tag_closings_1 = re.findall(tag_closing_1_regex, text)
        tag_closings_2 = re.findall(tag_closing_2_regex, text)

        openings_nr = len(tag_openings) - len(tag_closings_1)
        closings_nr = len(tag_closings_1) + len(tag_closings_2)

        if openings_nr == closings_nr:
            return True
        else:
            return False

    @staticmethod
    def is_opening_tag(text):
        tag_opening_regex = r'^\s*<[^/]+?>\s*$'

        match = re.match(tag_opening_regex, text)

        if match:
            return True
        else:
            return False

    @staticmethod
    def is_closing_tag(text):
        tag_closing_regex = r'^\s*</.+?>\s*$'

        match = re.match(tag_closing_regex, text)

        if match:
            return True
        else:
            return False

    @staticmethod
    def count_parts_to_tag(text_in_parts):
        parts_to_tag_nr = 0

        for part in text_in_parts:
            tag_regex = r'<.*?>'
            whitespace_regex = r'\s'

            cleaned_tags = re.sub(tag_regex, '', part)
            cleaned_whitespaces = re.sub(whitespace_regex, '', cleaned_tags)

            if cleaned_whitespaces:
                parts_to_tag_nr += 1

        return parts_to_tag_nr
