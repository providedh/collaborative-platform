import json
import logging


def log_adding_user_to_project(project_id, added_user_id, permissions, admin_id=None):
    logger = logging.getLogger('projects')

    message = f"User with id: {added_user_id} was added to project with id: {project_id} " \
              f"with permissions: '{permissions}'"

    if admin_id:
        message += f" by user with id: {admin_id}"

    logger.info(message)


def log_removing_user_from_project(project_id, admin_id, removed_user_id):
    logger = logging.getLogger('projects')

    logger.info(f"User with id: {removed_user_id} was removed from project with id: {project_id} by "
                f"user with id: {admin_id}")


def log_changing_user_permissions(project_id, admin_id, changed_user_id, old_permissions, new_permissions):
    logger = logging.getLogger('projects')

    logger.info(f"User with id: {admin_id} changed permissions of user with id: {changed_user_id} "
                f"in project with id: {project_id} from '{old_permissions}' to '{new_permissions}'")


def log_creating_project(project_id, user_id, project_settings):
    logger = logging.getLogger('projects')

    formatted_settings = json.dumps(project_settings, indent=4, sort_keys=True)

    logger.info(f"User with id: {user_id} created project with id: {project_id} "
                f"with parameters:\n{formatted_settings}")
