from apps.api_vis.db_handler import DbHandler

from apps.files_management.models import File


class RequestHandler:
    def __init__(self):
        pass

    def create_clique(self, project_id, user, request_data):
        db_handler = DbHandler(project_id, user)
        clique_id, clique_name = db_handler.create_clique(request_data)

        entities = request_data['entities']
        project_version_nr = request_data['project_version']
        certainty = request_data['certainty']
        unification_statuses = []

        for entity in entities:
            unification_status = {}

            if type(entity) is int:
                unification_status.update({'id': entity})
            elif type(entity) is dict:
                unification_status.update(entity)

            status_update = db_handler.add_unification(clique_id, entity, certainty, project_version_nr)
            unification_status.update(status_update)
            unification_statuses.append(unification_status)

        response = {
            'name': clique_name,
            'id': clique_id,
            'unification_statuses': unification_statuses,
        }

        return response

    def get_project_cliques(self, project_id, user, request_data):
        db_handler = DbHandler(project_id, user)
        response = db_handler.get_all_cliques_in_project(request_data)

        return response

    def delete_clique(self, project_id, user, request_data):
        db_handler = DbHandler(project_id, user)

        cliques = request_data['cliques']
        project_version_nr = request_data['project_version']
        delete_statuses = []

        for clique_id in cliques:
            delete_status = {}

            delete_status.update({'id': clique_id})

            status_update = db_handler.delete_clique(clique_id, project_version_nr)
            delete_status.update(status_update)
            delete_statuses.append(delete_status)

        response = {
            'delete_statuses': delete_statuses,
        }

        return response

    def get_file_cliques(self, file_id, user, request_data):
        project_id = File.objects.get(id=file_id).project_id

        db_handler = DbHandler(project_id, user)
        response = db_handler.get_all_cliques_which_include_entities_from_given_file(request_data, file_id)

        return response

    def get_project_entities(self, project_id, user, request_data):
        db_handler = DbHandler(project_id, user)
        response = db_handler.get_all_entities_in_project(request_data)

        return response

    def get_error_response(self, exception, status):
        response = {
            'status': status,
            'message': str(exception),
        }

        return response
