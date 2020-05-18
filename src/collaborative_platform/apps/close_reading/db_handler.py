from apps.close_reading.models import AnnotatingBodyContent
from apps.files_management.models import File, FileMaxXmlIds


class DbHandler:
    def __init__(self, user, file_id):
        self.__user = user
        self.__file = self.get_file_from_db(file_id)
        self.__annotating_body_content = self.__get_body_content_from_db()

    @staticmethod
    def get_file_from_db(file_id):
        file = File.objects.get(id=file_id, deleted=False)

        return file

    def __get_body_content_from_db(self):
        room_name = f'{self.__file.project.id}_{self.__file.id}'

        annotating_body_content = AnnotatingBodyContent.objects.get(file_symbol=room_name)

        return annotating_body_content

    def get_body_content(self):
        self.__annotating_body_content.refresh_from_db()
        body_content = self.__annotating_body_content.body_content

        return body_content

    def set_body_content(self, body_content):
        self.__annotating_body_content.body_content = body_content
        self.__annotating_body_content.save()

    def get_next_xml_id(self, entity_type):
        entity_max_xml_id = FileMaxXmlIds.objects.get(
            file=self.__file,
            xml_id_base=entity_type,
        )

        xml_id_nr = entity_max_xml_id.get_next_number()
        xml_id = f'{entity_type}-{xml_id_nr}'

        return xml_id

    def get_annotator_xml_id(self):
        annotator_xml_id = self.__user.profile.get_xml_id()

        return annotator_xml_id
