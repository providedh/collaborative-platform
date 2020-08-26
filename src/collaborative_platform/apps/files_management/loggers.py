import logging


class FilesManagementLogger:
    def __init__(self):
        self.__logger = logging.getLogger('files_management')

    def log_uploading_file(self, project_id, user_id, file_name, file_id):
        self.__logger.info(f"User with id: {user_id} upload file with name: {file_name} to "
                           f"project with id: {project_id}. File id: {file_id}")

    def log_deleting_file(self, project_id, user_id, file_id):
        self.__logger.info(f"User with id: {user_id} deleted file with id: {file_id} from "
                           f"project with id: {project_id}")
