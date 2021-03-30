from apps.api_vis.db_handler import DbHandler
from apps.api_vis.serializer import Serializer
from apps.exceptions import BadRequest, NotModified


class RequestHandler:
    def __init__(self, project_id, user):
        self.__db_handler = DbHandler(project_id, user)

    def serialize_entities(self, entities, project_version):
        return self.__serialize_entities(entities, project_version)

    def create_clique(self, request_data):
        clique_name = request_data.get('name')
        entities_ids = request_data['entities']
        project_version_nr = request_data['project_version']
        certainty = request_data['certainty']
        categories = request_data.get('categories')

        project_version = self.__db_handler.get_project_version_by_nr(project_version_nr)

        clique = self.__create_clique(clique_name, entities_ids, project_version)
        unification_statuses = self.__create_unifications(clique, entities_ids, certainty, categories, project_version)

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
        categories = request_data.get('categories')

        project_version = self.__db_handler.get_project_version_by_nr(project_version_nr)
        clique = self.__db_handler.get_clique(clique_id)

        unification_statuses = self.__create_unifications(clique, entities_ids, certainty, categories, project_version)

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

    def get_file_certainties(self, request_data, file_id):
        response = self.__get_certainties(request_data, file_id)

        return response

    def get_project_unbound_entities(self, request_data):
        response = self.__get_unbound_entities(request_data)

        return response

    def get_file_unbound_entities(self, file_id, request_data):
        response = self.__get_unbound_entities(request_data, file_id)

        return response

    def get_uncommitted_changes(self):
        uncommitted_changes = {}

        cliques_to_create = self.__db_handler.get_cliques_to_create()
        serialized_cliques = self.__serialize_uncommitted_cliques(cliques_to_create)
        uncommitted_changes.update({'cliques_to_create': serialized_cliques})

        cliques_to_delete = self.__db_handler.get_cliques_to_delete()
        serialized_cliques = self.__serialize_uncommitted_cliques(cliques_to_delete)
        uncommitted_changes.update({'cliques_to_delete': serialized_cliques})

        unifications_to_create = self.__db_handler.get_unifications_to_create()
        serialized_unifications = self.__serialize_uncommitted_unifications(unifications_to_create)
        uncommitted_changes.update({'unifications_to_add': serialized_unifications})

        unifications_to_delete = self.__db_handler.get_unifications_to_delete()
        serialized_unifications = self.__serialize_uncommitted_unifications(unifications_to_delete)
        uncommitted_changes.update({'unifications_to_remove': serialized_unifications})

        response = {
            'uncommitted_changes': uncommitted_changes
        }

        return response

    def __delete_cliques(self, cliques_ids, project_version):
        delete_statuses = []

        for clique_id in cliques_ids:
            delete_status = {'id': clique_id}

            status = self.__delete_clique(clique_id, project_version)

            delete_status.update(status)
            delete_statuses.append(delete_status)

        return delete_statuses

    def __create_unifications(self, clique, entities_ids, certainty, categories, project_version):
        unification_statuses = []

        for entity_id in entities_ids:
            unification_status = {}

            if type(entity_id) is int:
                unification_status.update({'id': entity_id})
            elif type(entity_id) is dict:
                unification_status.update(entity_id)

            status = self.__create_unification(clique, entity_id, certainty, categories, project_version)

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

    def __create_unification(self, clique, entity_id, certainty, categories, project_version):
        try:
            entity = self.__db_handler.get_entity_by_int_or_dict(entity_id)

            self.__db_handler.create_unification(clique, entity, certainty, categories, project_version)

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
        project_version = self.__db_handler.get_project_version(project_version_nr, date)
        serialized_entities = self.__serialize_entities(entities, project_version)

        return serialized_entities

    def __get_certainties(self, request_data, file_id=None):
        certainties = self.__db_handler.get_filtered_certainties(request_data, file_id)
        serialized_certainties = self.__serialize_certainties(certainties)

        # TODO: Append certainties created from unifications

        return serialized_certainties

    def __get_unbound_entities(self, request_data, file_id=None):
        project_version_nr = request_data.get('project_version')
        date = request_data.get('date')

        unbound_entities = self.__db_handler.get_filtered_unbound_entities(request_data, file_id)
        project_version = self.__db_handler.get_project_version(project_version_nr, date)
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

    @staticmethod
    def __serialize_uncommitted_cliques(cliques):
        serialized_cliques = []

        for clique in cliques:
            serialized_clique = {
                'id': clique.id,
                'name': clique.name,
                'created_by_id': clique.created_by.id,
                'type': clique.type
            }

            serialized_cliques.append(serialized_clique)

        return serialized_cliques

    def __serialize_uncommitted_unifications(self, unifications):
        serialized_unifications = []

        for unification in unifications:
            project_version = self.__db_handler.get_project_version_latest()
            entity_name = self.__db_handler.get_entity_property(unification.entity, project_version, 'name')
            categories = unification.categories.order_by('id')
            categories = categories.values_list('name', flat=True)
            categories = list(categories)

            serialized_unification = {
                'id': unification.id,
                'clique_id': unification.clique.id,
                'clique_name': unification.clique.name,
                'entity_id': unification.entity.id,
                'entity_name': entity_name.get_value(),
                'entity_xml_id': unification.entity.xml_id,
                'entity_type': unification.entity.type,
                'entity_file_name': unification.entity.file.name,
                'certainty': unification.certainty,
                'categories': categories,
                'created_by': unification.created_by.id,
            }

            serialized_unifications.append(serialized_unification)

        return serialized_unifications

    def __serialize_entities(self, entities, project_version):
        serialized_entities = []

        for entity in entities:
            serialized_entity = Serializer().serialize_entity(entity)

            entity_properties = self.__db_handler.get_entity_properties(entity, project_version)
            serialized_properties = Serializer().serialize_properties(entity_properties)

            serialized_entity.update({'properties': serialized_properties})
            serialized_entities.append(serialized_entity)

        return serialized_entities

    def __serialize_certainties(self, certainties):
        certainties_serialized = []

        for certainty in certainties:
            certainty_serialized = {
                'ana': certainty.get_categories(as_str=True),
                'locus': certainty.locus,
                'degree': certainty.degree,
                'cert': certainty.certainty,
                'resp': certainty.created_by.id,
                'match': certainty.target_match,
                'target': f'#{certainty.target_xml_id}',
                'xml:id': certainty.xml_id,
                'assertedValue': certainty.asserted_value,
                'desc': certainty.description,
                'file': certainty.file_id
            }

            certainties_serialized.append(certainty_serialized)

        return certainties_serialized
