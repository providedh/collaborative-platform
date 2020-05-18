

class XmlHandler:
    def __init__(self, user):
        self.__user = user

    def add_new_tag_to_text(self, text, xml_id, start_pos, end_pos):
        # TODO: Add verification if this same tag not existing already
        # TODO: Add possibility to add tag if text fragment is separated by another tag

        text_result = self.__add_tag(text, start_pos, end_pos, xml_id)

        return text_result

    def __add_tag(self, body_content, start_pos, end_pos, xml_id):
        text_before = body_content[:start_pos]
        text_inside = body_content[start_pos:end_pos]
        text_after = body_content[end_pos:]
        user_xml_id = self.__user.profile.get_xml_id()

        text_result = f'{text_before}<ab xml:id="{xml_id}" resp="#{user_xml_id}" saved="false">{text_inside}</ab>{text_after}'

        return text_result
