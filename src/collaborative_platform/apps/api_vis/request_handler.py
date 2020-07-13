from apps.api_vis.db_handler import DbHandler
from apps.api_vis.serializer import Serializer
from apps.exceptions import BadRequest, NotModified


class RequestHandler:
    def __init__(self, project_id, user):
        self.__db_handler = DbHandler(project_id, user)

    def create_clique(self, request_data):
        clique_name = request_data.get('name')
        entities_ids = request_data['entities']
        project_version_nr = request_data['project_version']
        certainty = request_data['certainty']

        project_version = self.__db_handler.get_project_version_by_nr(project_version_nr)

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

        project_version = self.__db_handler.get_project_version_by_nr(project_version_nr)
        clique = self.__db_handler.get_clique(clique_id)

        unification_statuses = self.__create_unifications(clique, entities_ids, certainty, project_version)

        response = {
            'unification_statuses': unification_statuses,
        }

        return response

    def delete_cliques(self, request_data):
        cliques_ids = request_data['cliques']
        project_version_nr = request_data['project_version']

        project_version = self.__db_handler.get_project_version_by_nr(project_version_nr)

        delete_statuses = self.__delete_cliques(cliques_ids, project_version)

        response = {
            'delete_statuses': delete_statuses,
        }

        return response

    def remove_entities_from_clique(self, clique_id, request_data):
        entities_ids = request_data['entities']
        project_version_nr = request_data['project_version']

        project_version = self.__db_handler.get_project_version_by_nr(project_version_nr)
        clique = self.__db_handler.get_clique(clique_id)

        delete_statuses = self.__delete_unifications(clique, entities_ids, project_version)

        response = {
            'delete_statuses': delete_statuses,
        }

        return response

    def create_commit(self, request_data):
        message = request_data.get('message')

        response = self.__create_commit(message)

        return response

    def get_project_cliques(self, request_data):
        response = self.__get_cliques(request_data)

        return response

    def get_file_cliques(self, request_data, file_id):
        response = self.__get_cliques(request_data, file_id)

        return response

    def get_project_entities(self, request_data):
        response = self.__get_entities(request_data)

        return response

    def get_file_entities(self, request_data, file_id):
        response = self.__get_entities(request_data, file_id)

        return response

    def get_project_unbound_entities(self, request_data):
        response = self.__get_unbound_entities(request_data)

        return response

    def get_file_unbound_entities(self, file_id, request_data):
        response = self.__get_unbound_entities(request_data, file_id)

        return response

    def get_uncommitted_changes(self, project_id, user):
        db_handler = DbHandler(project_id, user)
        response = db_handler.get_uncommitted_changes()

        return response

    def __delete_cliques(self, cliques_ids, project_version):
        delete_statuses = []

        for clique_id in cliques_ids:
            delete_status = {'id': clique_id}

            status = self.__delete_clique(clique_id, project_version)

            delete_status.update(status)
            delete_statuses.append(delete_status)

        return delete_statuses

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

    def __delete_unifications(self, clique, entities_ids, project_version):
        delete_statuses = []

        for entity_id in entities_ids:
            delete_status = {'id': entity_id}

            status = self.__delete_unification(clique, entity_id, project_version)

            delete_status.update(status)
            delete_statuses.append(delete_status)

        return delete_statuses

    def __create_clique(self, clique_name, entities_ids, project_version):
        first_entity = entities_ids[0]
        first_entity = self.__db_handler.get_entity_by_int_or_dict(first_entity)

        if not clique_name or clique_name == '':
            clique_name = self.__determine_clique_name(first_entity, project_version)

        clique_type = first_entity.type

        clique = self.__db_handler.create_clique(clique_name, clique_type)

        return clique

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

    def __delete_unification(self, clique, entity_id, project_version):
        try:
            entity = self.__db_handler.get_entity_by_int_or_dict(entity_id)
            unification = self.__db_handler.get_unification(clique, entity)

            if unification.deleted_in_commit is not None:
                raise NotModified(f"Entity with id: {entity.id} is already removed from clique with id: {clique.id}")

            self.__db_handler.delete_unification(unification, project_version, save=True)

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

    def __create_commit(self, message):
        try:
            self.__db_handler.create_commit(message)

            status = {
                'status': 200,
                'message': 'OK'
            }

        except NotModified as exception:
            status = {
                'status': NotModified.status_code,
                'message': str(exception)
            }

        return status

    def __determine_clique_name(self, entity, project_version):
        entity_name = self.__db_handler.get_entity_property(entity, project_version, 'name')
        clique_name = entity_name.get_value(as_str=True)

        return clique_name

    def __get_cliques(self, request_data, file_id=None):
        cliques = self.__db_handler.get_filtered_cliques(request_data, file_id)
        serialized_cliques = self.__serialize_cliques(cliques, request_data)

        return serialized_cliques

    def __get_entities(self, request_data, file_id=None):
        project_version_nr = request_data.get('project_version')
        date = request_data.get('date')

        entities = self.__db_handler.get_filtered_entities(request_data, file_id)
        project_version = self.__get_project_version(project_version_nr, date)
        serialized_entities = self.__serialize_entities(entities, project_version)

        return serialized_entities

    def __get_unbound_entities(self, request_data, file_id=None):
        project_version_nr = request_data.get('project_version')
        date = request_data.get('date')

        unbound_entities = self.__db_handler.get_filtered_unbound_entities(request_data, file_id)
        project_version = self.__get_project_version(project_version_nr, date)
        serialized_entities = self.__serialize_entities(unbound_entities, project_version)

        return serialized_entities

    def __serialize_cliques(self, cliques, request_data):
        serialized_cliques = []

        for clique in cliques:
            serialized_clique = Serializer().serialize_clique(clique)

            unifications = self.__db_handler.get_filtered_unifications(request_data, clique)
            entities_ids = Serializer().get_entities_ids(unifications)

            serialized_clique.update({'entities': entities_ids})
            serialized_cliques.append(serialized_clique)

        return serialized_cliques

    def __serialize_entities(self, entities, project_version):
        serialized_entities = []

        for entity in entities:
            serialized_entity = Serializer().serialize_entity(entity)

            entity_name = self.__db_handler.get_entity_property(entity, project_version, 'name')
            entity_name = entity_name.get_value(as_str=True)

            serialized_entity.update({'name': entity_name})
            serialized_entities.append(serialized_entity)

        return serialized_entities

    def __get_project_version(self, project_version_nr, date):
        if project_version_nr:
            project_version = self.__db_handler.get_project_version_by_nr(project_version_nr)

        elif date:
            project_version = self.__db_handler.get_project_version_by_date(date)

        else:
            project_version = self.__db_handler.get_project_version()

        return project_version
