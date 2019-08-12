from .corrector import AbstractCorrector


class CorrectorLanguage(AbstractCorrector):
    def __init__(self):
        super().__init__()
        self.name_of_correction = "language"

    def _get_declarations_to_switch(self, attribute_name, attribute_value):
        if attribute_value == '"english"':
            wrong_language = attribute_value
            wrong_language = wrong_language.replace('"', '')

            correct_language = "en"

        else:
            raise ValueError("Unknown {} format: {}. Add new instruction to 'CorrectorLanguage' class".format(
                self.name_of_correction, attribute_value))

        old_declaration = attribute_name + '="' + wrong_language + '"'
        new_declaration = attribute_name + '="' + correct_language + '"'

        return old_declaration, new_declaration
