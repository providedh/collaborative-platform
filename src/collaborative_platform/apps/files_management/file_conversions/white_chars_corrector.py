
CR_LF_CODES = ['&#xa;', '&#xd;', '&#10;', '&#13;']
NON_UNIX_NEWLINES = ['\r', '\r\n']


class WhiteCharsCorrector:
    def __init__(self):
        pass

    def check_if_cr_lf_codes(self, text):
        for code in CR_LF_CODES:
            if code in text:
                return True

        return False

    def replace_cr_lf_codes(self, text):
        text_corrected = text
        for code in CR_LF_CODES:
            text_corrected = text_corrected.replace(code, '<lb/>')

        return text_corrected

    def check_if_non_unix_newlines(self, text):
        for newline in NON_UNIX_NEWLINES:
            if newline in text:
                return True

        return False

    def normalize_newlines(self, text):
        text_in_lines = text.splitlines()
        text_normalized = '\n'.join(text_in_lines)

        return text_normalized
