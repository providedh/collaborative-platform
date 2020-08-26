import logging


class FilesManagementLogger:
    def __init__(self):
        self.__logger = logging.getLogger('files_management')

    def log_uploading_file(self, project_id, user_id, file_name, file_id):
        self.__logger.info(f"User with id: {user_id} upload file with name: {file_name} to "
                           f"project with id: {project_id}. File id: {file_id}")

    def log_uploading_file_error(self, file_name, message):
        self.__logger.exception(f"Uploading of file: {file_name} caused unhandled exception: {message}")

    def log_migrating_file(self, old_file_id, new_file_id, message):
        self.__logger.info(f"File with id: {new_file_id} was migrated. New file id: {old_file_id}. "
                           f"Migration message: {message}")

    def log_deleting_file(self, project_id, user_id, file_id):
        self.__logger.info(f"User with id: {user_id} deleted file with id: {file_id} from "
                           f"project with id: {project_id}")
