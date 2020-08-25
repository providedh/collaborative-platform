import json
import logging


class ProjectsLogger:
    def __init__(self):
        self.__logger = logging.getLogger('projects')

    def log_adding_user_to_project(self, project_id, added_user_id, permissions, admin_id=None):
        message = f"User with id: {added_user_id} was added to project with id: {project_id} " \
                  f"with permissions: '{permissions}'"

        if admin_id:
            message += f" by user with id: {admin_id}"

        self.__logger.info(message)

    def log_removing_user_from_project(self, project_id, admin_id, removed_user_id):
        self.__logger.info(f"User with id: {removed_user_id} was removed from project with id: {project_id} by "
                           f"user with id: {admin_id}")

    def log_changing_user_permissions(self, project_id, admin_id, changed_user_id, old_permissions, new_permissions):
        self.__logger.info(f"User with id: {admin_id} changed permissions of user with id: {changed_user_id} "
                           f"in project with id: {project_id} from '{old_permissions}' to '{new_permissions}'")

    def log_creating_project(self, project_id, user_id, project_settings):
        formatted_settings = json.dumps(project_settings, indent=4, sort_keys=True)

        self.__logger.info(f"User with id: {user_id} created project with id: {project_id} "
                           f"with parameters:\n{formatted_settings}")


class FilesManagementLogger:
    def __init__(self):
        self.__logger = logging.getLogger('files_management')

    def log_uploading_file(self, project_id, user_id, file_name, file_id):
        self.__logger.info(f"User with id: {user_id} upload file with name: {file_name} to "
                           f"project with id: {project_id}. File id: {file_id}")

    def log_deleting_file(self, project_id, user_id, file_id):
        self.__logger.info(f"User with id: {user_id} deleted file with id: {file_id} from "
                           f"project with id: {project_id}")


class CloseReadingLogger:
    def __init__(self):
        self.__logger = logging.getLogger('close_reading')

    def log_removing_users_room_presence_table(self, user_id, room_symbol):
        self.__logger.info(f"User with id: '{user_id}' was removed from room: {room_symbol}  due to inactivity")

    def log_number_of_remaining_users_in_room(self, room_symbol, users_number):
        self.__logger.info(f"In room: '{room_symbol}' left: {users_number} users")

    def log_pruning_body_content(self, file_id, room_symbol):
        self.__logger.info(f"Content of <body> element of file with id: '{file_id}' removed from room: '{room_symbol}'")
