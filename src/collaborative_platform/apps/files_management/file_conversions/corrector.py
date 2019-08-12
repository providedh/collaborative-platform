from abc import ABC, abstractmethod


class AbstractCorrector(ABC):
    def __init__(self):
        self._corrector_type = ""

    def get_corrected_tag(self, tag_text, attributes_to_correct):
        corrected_tag = tag_text

        for attribute_to_correct in attributes_to_correct:
            attribute_value = attribute_to_correct['wrong_value']
            attribute_name = attribute_to_correct['argument']

            old_declaration, new_declaration = self._get_declarations_to_switch(attribute_name, attribute_value)

            corrected_tag = corrected_tag.replace(old_declaration, new_declaration)

        return corrected_tag

    @abstractmethod
    def _get_declarations_to_switch(self, attribute_name, attribute_value):
        pass
