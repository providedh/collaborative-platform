from apps.close_reading.models import AnnotatingBodyContent
from apps.files_management.models import File


class DbHandler:
    def __init__(self, user, file_id):
        self.__user = user
        self.__file = None

        self.__get_file_from_db(file_id)
        self.__get_body_content_from_db()

    def __get_file_from_db(self, file_id):
        self.__file = File.objects.get(id=file_id, deleted=False)

    def __get_body_content_from_db(self):
        room_name = f'{self.__file.project.id}_{self.__file.id}'

        self.__annotating_body_content = AnnotatingBodyContent.objects.get(file_symbol=room_name)

    def get_body_content(self):
        self.__annotating_body_content.refresh_from_db()
        body_content = self.__annotating_body_content.body_content

        return body_content

    def set_body_content(self, body_content):
        self.__annotating_body_content.body_content = body_content
        self.__annotating_body_content.save()
