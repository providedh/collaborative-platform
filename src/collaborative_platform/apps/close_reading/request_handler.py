import json

from apps.files_management.models import File


class RequestHandler:
    def __init__(self, file_id):
        self.__file = None

        self.__get_file_from_db(file_id)

    def __get_file_from_db(self, file_id):
        self.__file = File.objects.get(id=file_id, deleted=False)

    def handle_request(self, text_data, user):
        request = self.__parse_text_data(text_data)

        for operation in request:
            # update file





            # update database
            pass






    def __parse_text_data(self, text_data):
        request = json.loads(text_data)

        return request
