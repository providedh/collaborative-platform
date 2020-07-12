from apps.api_vis.db_handler import DbHandler
from apps.exceptions import BadRequest, NotModified
from apps.files_management.models import File
from apps.api_vis.models import Clique


class RequestHandler:
    def __init__(self, project_id, user):
        self.__db_handler = DbHandler(project_id, user)

    def create_clique(self, request_data):
        clique_name = request_data.get('name')
        entities_ids = request_data['entities']
        project_version_nr = request_data['project_version']
        certainty = request_data['certainty']

        project_version = self.__db_handler.get_project_version(project_version_nr)

        clique = self.__create_clique(clique_name, entities_ids, project_version)
        unification_statuses = self.__create_unifications(clique, entities_ids, certainty, project_version)

        response = {
            'name': clique.name,
            'id': clique.id,
            'unification_statuses': unification_statuses,
        }

        return response

    def add_entities_to_clique(self, clique_id, request_data):
        entities_ids = request_data['entities']
        project_version_nr = request_data['project_version']
        certainty = request_data['certainty']

        project_version = self.__db_handler.get_project_version(project_version_nr)
        clique = self.__db_handler.get_clique(clique_id)

        unification_statuses = self.__create_unifications(clique, entities_ids, certainty, project_version)

        response = {
            'unification_statuses': unification_statuses,
        }

        return response

    def delete_cliques(self, request_data):
        cliques_ids = request_data['cliques']
        project_version_nr = request_data['project_version']

        project_version = self.__db_handler.get_project_version(project_version_nr)

        delete_statuses = self.__delete_cliques(cliques_ids, project_version)

        response = {
            'delete_statuses': delete_statuses,
        }

        return response

    def remove_entities_from_clique(self, clique_id, user, request_data):
        project_id = Clique.objects.get(id=clique_id).project_id

        db_handler = DbHandler(project_id, user)

        entities_ids = request_data['entities']
        project_version_nr = request_data['project_version']
        delete_statuses = []

        for entity_id in entities_ids:
            delete_status = {}

            delete_status.update({'id': entity_id})

            status_update = db_handler.delete_unification(clique_id, entity_id, project_version_nr)
            delete_status.update(status_update)
            delete_statuses.append(delete_status)

        response = {
            'delete_statuses': delete_statuses,
        }

        return response

    def get_project_cliques(self, project_id, user, request_data):
        db_handler = DbHandler(project_id, user)
        response = db_handler.get_all_cliques_in_project(request_data)

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

    def get_file_entities(self, file_id, user, request_data):
        project_id = File.objects.get(id=file_id).project_id

        db_handler = DbHandler(project_id, user)
        response = db_handler.get_all_entities_in_file(request_data, file_id)

        return response

    def get_project_unbound_entities(self, project_id, user, request_data):
        db_handler = DbHandler(project_id, user)
        response = db_handler.get_unbound_entities_in_project(request_data)

        return response

    def get_file_unbound_entities(self, file_id, user, request_data):
        project_id = File.objects.get(id=file_id).project_id

        db_handler = DbHandler(project_id, user)
        response = db_handler.get_unbound_entities_in_file(request_data, file_id)

        return response

    def create_commit(self, project_id, user, request_data):
        message = request_data.get('message')

        db_handler = DbHandler(project_id, user)
        db_handler.commit_changes(message)

        response = {
            'status': 200,
            'message': 'OK'
        }

        return response

    def get_uncommitted_changes(self, project_id, user):
        db_handler = DbHandler(project_id, user)
        response = db_handler.get_uncommitted_changes()

        return response

    def __determine_clique_name(self, entity, project_version):
        entity_name = self.__db_handler.get_entity_property(entity, project_version, 'name')
        clique_name = entity_name.get_value(as_str=True)

        return clique_name

    def __determine_clique_type(self, entity):
        entity_type = entity.type

        return entity_type

    def __create_clique(self, clique_name, entities_ids, project_version):
        first_entity = entities_ids[0]
        first_entity = self.__db_handler.get_entity_by_int_or_dict(first_entity)

        if not clique_name or clique_name == '':
            clique_name = self.__determine_clique_name(first_entity, project_version)

        clique_type = self.__determine_clique_type(first_entity)

        clique = self.__db_handler.create_clique(clique_name, clique_type)

        return clique

    def __create_unifications(self, clique, entities_ids, certainty, project_version):
        unification_statuses = []

        for entity_id in entities_ids:
            unification_status = {}

            if type(entity_id) is int:
                unification_status.update({'id': entity_id})
            elif type(entity_id) is dict:
                unification_status.update(entity_id)

            status = self.__create_unification(clique, entity_id, certainty, project_version)

            unification_status.update(status)
            unification_statuses.append(unification_status)

        return unification_statuses

    def __create_unification(self, clique, entity_id, certainty, project_version):
        try:
            entity = self.__db_handler.get_entity_by_int_or_dict(entity_id)

            self.__db_handler.create_unification(clique, entity, certainty, project_version)

            status = {
                'status': 200,
                'message': 'OK'
            }

        except BadRequest as exception:
            status = {
                'status': 400,
                'message': str(exception)
            }

        return status

    def __delete_cliques(self, cliques_ids, project_version):
        delete_statuses = []

        for clique_id in cliques_ids:
            delete_status = {'id': clique_id}

            status = self.__delete_clique(clique_id, project_version)

            delete_status.update(status)
            delete_statuses.append(delete_status)

        return delete_statuses

    def __delete_clique(self, clique_id, project_version):
        try:
            clique = self.__db_handler.get_clique(clique_id)

            if clique.deleted_in_commit is not None:
                raise NotModified(f"Clique with id: {clique.id} is already deleted.")

            self.__db_handler.delete_clique(clique, project_version)

            status = {
                'status': 200,
                'message': 'OK'
            }

        except BadRequest as exception:
            status = {
                'status': BadRequest.status_code,
                'message': str(exception)
            }

        except NotModified as exception:
            status = {
                'status': NotModified.status_code,
                'message': str(exception)
            }

        return status
