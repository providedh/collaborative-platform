from copy import deepcopy

from django.db.models import Q
from django.forms.models import model_to_dict
from django.utils import timezone

from apps.api_vis.models import Clique, Commit, Entity, EntityProperty, EntityVersion, Unification
from apps.api_vis.helpers import parse_project_version
from apps.api_vis.request_validator import validate_keys_and_types
from apps.exceptions import BadRequest, NotModified
from apps.files_management.models import Directory, File, FileVersion
from apps.projects.models import ProjectVersion


class DbHandler:
    def __init__(self, project_id, user):
        self.__project_id = project_id
        self.__user = user

    def get_all_cliques_in_project(self, qs_parameters):
        serialized_cliques = self.__get_serialized_cliques(qs_parameters)

        return serialized_cliques

    def __get_serialized_cliques(self, qs_parameters, file_id=None):
        cliques = self.__get_filtered_cliques(qs_parameters, file_id)

        serialized_cliques = []

        for clique in cliques:
            unifications = self.__get_filtered_unifications(qs_parameters, clique)

            serialized_clique = model_to_dict(clique, ['id', 'name', 'type'])

            entities_ids = unifications.values_list('entity_id', flat=True)
            entities_ids = list(entities_ids)

            serialized_clique.update({'entities': entities_ids})
            serialized_cliques.append(serialized_clique)

        return serialized_cliques

    def get_all_cliques_which_include_entities_from_given_file(self, qs_parameters, file_id):
        serialized_cliques = self.__get_serialized_cliques(qs_parameters, file_id)

        return serialized_cliques

    def get_all_entities_in_project(self, qs_parameters):
        serialized_entities = self.__get_serialized_entities(qs_parameters)

        return serialized_entities

    def get_all_entities_in_file(self, qs_parameters, file_id):
        serialized_entities = self.__get_serialized_entities(qs_parameters, file_id)

        return serialized_entities

    def __get_serialized_entities(self, qs_parameters, file_id=None):
        entities = self.__get_filtered_entities(qs_parameters, file_id)

        serialized_entities = []

        for entity in entities:
            serialized_entity = model_to_dict(entity, ['id', 'type'])

            try:
                entity_name = entity.versions.latest('id').properties.get(name='name').get_value()

            except EntityProperty.DoesNotExist:
                entity_name = None

            serialized_entity.update({'name': entity_name})
            serialized_entities.append(serialized_entity)

        return serialized_entities

    def get_unbound_entities_in_project(self, qs_parameters):
        serialized_entities = self.__get_serialized_unbound_entities(qs_parameters)

        return serialized_entities

    def get_unbound_entities_in_file(self, qs_parameters, file_id):
        serialized_entities = self.__get_serialized_unbound_entities(qs_parameters, file_id)

        return serialized_entities

    def __get_serialized_unbound_entities(self, qs_parameters, file_id=None):
        parameters_for_entities = deepcopy(qs_parameters)
        parameters_for_entities.pop('users', None)

        entities = self.__get_filtered_entities(parameters_for_entities, file_id)
        unifications = self.__get_filtered_unifications(qs_parameters)

        bound_entities_ids = []

        for unification in unifications:
            bound_entities_ids.append(unification.entity.id)

        bound_entities_ids = set(bound_entities_ids)

        entities = entities.exclude(id__in=bound_entities_ids)

        serialized_entities = []

        for entity in entities:
            serialized_entity = model_to_dict(entity, ['id', 'type'])

            try:
                entity_name = entity.versions.latest('id').properties.get(name='name').get_value()

            except EntityProperty.DoesNotExist:
                entity_name = None

            serialized_entity.update({'name': entity_name})
            serialized_entities.append(serialized_entity)

        return serialized_entities

    def __get_filtered_cliques(self, qs_parameters, file_id=None):
        cliques = Clique.objects.filter(
            project_id=self.__project_id,
            created_in_commit__isnull=False,
        )

        if file_id:
            cliques = cliques.filter(
                unifications__entity__file_id=file_id,
            )

        if 'types' in qs_parameters:
            cliques = cliques.filter(type__in=qs_parameters['types'])

        if 'users' in qs_parameters:
            cliques = cliques.filter(created_by_id__in=qs_parameters['users'])

        if 'start_date' in qs_parameters:
            cliques = cliques.filter(unifications__created_on__gte=qs_parameters['start_date'])

        if 'end_date' in qs_parameters:
            cliques = cliques.filter(unifications__created_on__lte=qs_parameters['end_date'])

        if 'date' in qs_parameters:
            date = qs_parameters['date']

            project_version = ProjectVersion.objects.filter(
                project_id=self.__project_id,
                date__lte=date,
                commit__isnull=False,
            ).latest('id')

            commit = project_version.commit

            cliques = cliques.filter(
                Q(unifications__deleted_in_commit_id__gte=commit.id) | Q(unifications__deleted_in_commit__isnull=True),
                unifications__created_in_commit_id__lte=commit.id,
            )

        elif 'project_version' in qs_parameters:
            project_version_nr = qs_parameters['project_version']
            file_version_counter, commit_counter = parse_project_version(project_version_nr)

            project_version = ProjectVersion.objects.get(
                project_id=self.__project_id,
                commit_counter=commit_counter,
                commit__isnull=False,
            )

            commit = project_version.commit

            cliques = cliques.filter(
                Q(unifications__deleted_in_commit_id__gte=commit.id) | Q(unifications__deleted_in_commit__isnull=True),
                unifications__created_in_commit_id__lte=commit.id,
            )

        else:
            cliques = cliques.filter(deleted_in_commit__isnull=True)

        cliques = cliques.distinct().order_by('id')

        return cliques

    def __get_filtered_unifications(self, qs_parameters, clique=None):
        if clique:
            unifications = clique.unifications

        else:
            unifications = Unification.objects.filter(
                project_id=self.__project_id,
                created_in_commit__isnull=False,
            )

        if 'users' in qs_parameters:
            unifications = unifications.filter(created_by_id__in=qs_parameters['users'])

        if 'start_date' in qs_parameters:
            unifications = unifications.filter(created_on__gte=qs_parameters['start_date'])

        if 'end_date' in qs_parameters:
            unifications = unifications.filter(created_on__lte=qs_parameters['end_date'])

        if 'date' in qs_parameters:
            unifications = unifications.filter(
                Q(deleted_on__gte=qs_parameters['date']) | Q(deleted_on__isnull=True),
                created_on__lte=qs_parameters['date'],
            )

        elif 'project_version' in qs_parameters:
            project_version_nr = qs_parameters['project_version']
            file_version_counter, commit_counter = parse_project_version(project_version_nr)

            project_version = ProjectVersion.objects.get(
                project_id=self.__project_id,
                commit_counter=commit_counter,
                commit__isnull=False,
            )

            commit = project_version.commit

            unifications = unifications.filter(
                Q(deleted_in_commit_id__gte=commit.id) | Q(deleted_in_commit_id__isnull=True),
                created_in_commit_id__lte=commit.id,
            )

        else:
            unifications = unifications.filter(deleted_in_commit__isnull=True)

        unifications = unifications.order_by('id')

        return unifications

    def __get_filtered_entities(self, qs_parameters, file_id=None):
        entities = Entity.objects.filter(
            file__project_id=self.__project_id,
            created_in_file_version__isnull=False,
        )

        if file_id:
            entities = entities.filter(file_id=file_id)

        if 'types' in qs_parameters:
            entities = entities.filter(type__in=qs_parameters['types'])

        if 'users' in qs_parameters:
            entities = entities.filter(created_by_id__in=qs_parameters['users'])

        if 'project_version' in qs_parameters:
            project_version_nr = qs_parameters['project_version']
            file_version_counter, commit_counter = parse_project_version(project_version_nr)

            project_version = ProjectVersion.objects.get(
                project_id=self.__project_id,
                commit_counter=commit_counter,
                file_version_counter=file_version_counter
            )

            file_versions_ids = project_version.file_versions.values_list('id', flat=True)

            entities = entities.filter(
                versions__file_version_id__in=file_versions_ids
            )

        elif 'date' in qs_parameters:
            date = qs_parameters['date']

            project_version = ProjectVersion.objects.filter(
                project_id=self.__project_id,
                date__lte=date,
                commit__isnull=False,
            ).latest('id')

            file_versions_ids = project_version.file_versions.values_list('id', flat=True)

            entities = entities.filter(
                versions__file_version_id__in=file_versions_ids
            )

        else:
            entities = entities.filter(deleted_in_file_version__isnull=True)

        entities = entities.order_by('id')

        return entities

    def create_clique(self, clique_name, clique_type):
        clique = self.__create_clique(clique_name, clique_type)

        return clique

    def __get_clique_type(self, request_entities):
        entity_type = None

        for entity in request_entities:
            try:
                entity = self.get_entity_by_int_or_dict(entity)

            except BadRequest:
                continue

            else:
                entity_type = entity.type

        if entity_type:
            return entity_type

        else:
            raise BadRequest("Can't get entity type from provided entity ids")

    def delete_unification(self, clique_id, entity_id, project_version_nr):
        try:
            unification = self.__get_unification_from_db(clique_id, entity_id)

            if unification.deleted_in_commit is not None:
                raise NotModified(f"Entity with id: {entity_id} is already removed from clique with id: {clique_id}")

            self.__mark_unification_to_delete(unification, project_version_nr)

            delete_status = {
                'status': 200,
                'message': 'OK'
            }

        except NotModified as exception:
            delete_status = {
                'status': 304,
                'message': str(exception)
            }

        except BadRequest as exception:
            delete_status = {
                'status': 400,
                'message': str(exception)
            }

        return delete_status

    def __mark_unification_to_delete(self, unification, project_version_nr):
        project_version = self.get_project_version(project_version_nr)

        file_version = project_version.file_versions.get(
            file=unification.entity.file
        )

        unification.deleted_by = self.__user
        unification.deleted_on = timezone.now()
        unification.deleted_in_file_version = file_version
        unification.save()

    @staticmethod
    def __get_unification_from_db(clique_id, entity_id):
        try:
            unification = Unification.objects.get(
                clique_id=clique_id,
                entity_id=entity_id
            )
        except Unification.DoesNotExist:
            raise BadRequest(f"Clique with id: {clique_id} doesn't contain entity with id: {entity_id}")

        return unification

    def get_clique(self, clique_id):
        try:
            clique = Clique.objects.get(
                id=clique_id,
            )

        except Clique.DoesNotExist:
            raise BadRequest(f"Clique with id: {clique_id} doesn't exist in project with id: {self.__project_id}")

        return clique

    def delete_clique(self, clique, project_version):
        delete_time = timezone.now()

        clique.deleted_by = self.__user
        clique.deleted_on = delete_time
        clique.save()

        self.delete_unifications(clique, project_version, delete_time)

    def delete_unifications(self, clique, project_version, delete_time):
        unifications = clique.unifications.filter(
            deleted_in_commit__isnull=True
        )

        for unification in unifications:
            file_version = project_version.file_versions.get(
                file=unification.entity.file
            )

            unification.deleted_by = self.__user
            unification.deleted_on = delete_time
            unification.deleted_in_file_version = file_version

        Unification.objects.bulk_update(unifications, ['deleted_by', 'deleted_on', 'deleted_in_file_version'])

    def __get_clique_name(self, request_data):
        clique_name = request_data.get('name')

        if not clique_name or clique_name == '':
            request_entity = request_data.get('entities')[0]
            entity = self.get_entity_by_int_or_dict(request_entity)

            project_version_nr = request_data.get('project_version')
            project_version = self.get_project_version(project_version_nr)

            file_version = project_version.file_versions.get(
                file=entity.file
            )

            entity_name = EntityProperty.objects.get(
                name='name',
                entity=entity,
                entity_version__file_version=file_version
            )

            clique_name = entity_name.get_value()

        return clique_name

    def get_entity_version(self, entity, project_version):
        file_version = project_version.file_versions.get(
            file=entity.file
        )

        entity_version = EntityVersion.objects.get(
            entity=entity,
            file_version=file_version
        )

        return entity_version

    def get_entity_property(self, entity, project_version, property_name):
        entity_version = self.get_entity_version(entity, project_version)

        property_version = entity_version.properties.get(
            name=property_name
        )

        return property_version

    def __create_clique(self, clique_name, clique_type):
        clique = Clique.objects.create(
            project_id=self.__project_id,
            name=clique_name,
            type=clique_type,
            created_by=self.__user,
        )

        return clique

    def get_project_version(self, project_version_nr):
        file_version_counter, commit_counter = parse_project_version(project_version_nr)

        try:
            project_version = ProjectVersion.objects.get(
                project_id=self.__project_id,
                file_version_counter=file_version_counter,
                commit_counter=commit_counter,
            )
        except ProjectVersion.DoesNotExist:
            raise BadRequest(f"Version: {project_version_nr} of project with id: {self.__project_id} doesn't exist.")

        return project_version

    def create_unification(self, clique, entity, certainty, project_version):
        file_version = FileVersion.objects.get(
            projectversion=project_version,
            file=entity.file
        )

        unification = Unification.objects.create(
            project=project_version.project,
            entity=entity,
            clique=clique,
            certainty=certainty,
            created_by=self.__user,
            created_in_file_version=file_version
        )

        return unification

    def get_entity_by_int_or_dict(self, request_entity):
        if type(request_entity) == int:
            try:
                entity = Entity.objects.get(
                    id=request_entity,
                )

                return entity

            except Entity.DoesNotExist:
                raise BadRequest(f"Entity with id: {request_entity} doesn't exist in project with id: "
                                 f"{self.__project_id}.")

        elif type(request_entity) == dict:
            required_keys = {
                'file_path': str,
                'xml_id': str,
            }

            validate_keys_and_types(request_entity, required_keys, parent_name="entity")

            file_path = request_entity['file_path']
            xml_id = request_entity['xml_id']

            file_id = self.get_file_id_from_path(file_path)

            try:
                entity = Entity.objects.get(
                    file__project_id=self.__project_id,
                    file_id=file_id,
                    xml_id=xml_id,
                )

                return entity

            except Entity.DoesNotExist:
                file_name = request_entity['file_path'].split('/')[-1]
                raise BadRequest(f"Entity with xml:id: {xml_id} doesn't exist in file: {file_name}.")

        else:
            raise BadRequest(f"Invalid type of 'entity' parameter. Allowed types is '{str(int)}' and {str(dict)}.")

    def get_file_id_from_path(self, file_path, parent_directory_id=None):
        splitted_path = file_path.split('/')

        if len(splitted_path) == 1:
            file_name = splitted_path[0]

            try:
                file = File.objects.get(
                    project_id=self.__project_id,
                    parent_dir_id=parent_directory_id,
                    name=file_name,
                    deleted=False
                )

                return file.id

            except File.DoesNotExist:
                raise BadRequest(f"File with name {file_name} doesn't exist in this directory.")

        else:
            directory_name = splitted_path[0]

            try:
                directory = Directory.objects.get(
                    project_id=self.__project_id,
                    parent_dir_id=parent_directory_id,
                    name=directory_name)
                rest_of_path = '/'.join(splitted_path[1:])

                return self.get_file_id_from_path(rest_of_path, directory.id)

            except Directory.DoesNotExist:
                raise BadRequest(f"Directory with name {directory_name} does't exist in this directory.")

    def commit_changes(self, message):
        cliques_to_create = self.__get_cliques_to_create_from_db()
        unifications_to_add = self.__get_unifications_to_add_from_db()
        cliques_to_delete = self.__get_cliques_to_delete_from_db()
        unifications_to_delete = self.__get_unifications_to_remove_from_db()

        if len(cliques_to_create) + len(unifications_to_add) + len(cliques_to_delete) + len(unifications_to_delete) == 0:
            raise NotModified(f'You dont have any changes to commit in project with id: {self.__project_id}.')

        commit = Commit.objects.create(
            project_id=self.__project_id,
            message=message if message else ''
        )

        for clique in cliques_to_create:
            clique.created_in_commit = commit

        Clique.objects.bulk_update(cliques_to_create, ['created_in_commit'])

        for clique in cliques_to_delete:
            clique.deleted_in_commit = commit

        Clique.objects.bulk_update(cliques_to_delete, ['deleted_in_commit'])

        for unification in unifications_to_add:
            unification.created_in_commit = commit

        Unification.objects.bulk_update(unifications_to_add, ['created_in_commit'])

        for unification in unifications_to_delete:
            unification.deleted_in_commit = commit

        Unification.objects.bulk_update(unifications_to_delete, ['deleted_in_commit'])

    def get_uncommitted_changes(self):
        cliques_to_create = self.__get_cliques_to_create_from_db()
        unifications_to_add = self.__get_unifications_to_add_from_db()
        cliques_to_delete = self.__get_cliques_to_delete_from_db()
        unifications_to_remove = self.__get_unifications_to_remove_from_db()

        response = {
            'uncommitted_changes': {
                'cliques_to_create': [],
                'cliques_to_delete': [],
                'unifications_to_add': [],
                'unifications_to_remove': [],
            }
        }

        for clique in cliques_to_create:
            serialized_clique = {
                'id': clique.id,
                'name': clique.name,
                'created_by_id': clique.created_by.id
            }

            response['uncommitted_changes']['cliques_to_create'].append(serialized_clique)

        for clique in cliques_to_delete:
            serialized_clique = {
                'id': clique.id,
                'name': clique.name,
                'created_by_id': clique.created_by.id
            }

            response['uncommitted_changes']['cliques_to_delete'].append(serialized_clique)

        for unification in unifications_to_add:
            entity_version = EntityVersion.objects.get(
                entity=unification.entity,
                file_version=unification.created_in_file_version,
            )

            entity_name = entity_version.properties.get(
                name='name'
            )

            serialized_unification = {
                'id': unification.id,
                'clique_id': unification.clique.id,
                'clique_name': unification.clique.name,
                'entity_id': unification.entity.id,
                'entity_name': entity_name.get_value(),
                'certainty': unification.certainty,
                'created_by': unification.created_by.id,
            }

            response['uncommitted_changes']['unifications_to_add'].append(serialized_unification)

        for unification in unifications_to_remove:
            entity_version = EntityVersion.objects.get(
                entity=unification.entity,
                file_version=unification.created_in_file_version,
            )

            entity_name = entity_version.properties.get(
                name='name'
            )

            serialized_unification = {
                'id': unification.id,
                'clique_id': unification.clique.id,
                'clique_name': unification.clique.name,
                'entity_id': unification.entity.id,
                'entity_name': entity_name.get_value(),
                'certainty': unification.certainty,
                'created_by': unification.created_by.id,
            }

            response['uncommitted_changes']['unifications_to_remove'].append(serialized_unification)

        return response

    def __get_cliques_to_create_from_db(self):
        cliques_to_create = Clique.objects.filter(
            project_id=self.__project_id,
            created_by=self.__user,
            created_in_commit__isnull=True,
        )

        return cliques_to_create

    def __get_unifications_to_add_from_db(self):
        unifications_to_add = Unification.objects.filter(
            project_id=self.__project_id,
            created_by=self.__user,
            created_in_commit__isnull=True
        )

        return unifications_to_add

    def __get_cliques_to_delete_from_db(self):
        cliques_to_delete = Clique.objects.filter(
            project_id=self.__project_id,
            deleted_by=self.__user,
            created_in_commit__isnull=False,
            deleted_in_commit__isnull=True,
        )

        return cliques_to_delete

    def __get_unifications_to_remove_from_db(self):
        unifications_to_delete = Unification.objects.filter(
            project_id=self.__project_id,
            deleted_by=self.__user,
            created_in_commit__isnull=False,
            deleted_in_commit__isnull=True,
        )

        return unifications_to_delete

