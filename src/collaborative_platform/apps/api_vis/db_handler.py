from django.forms.models import model_to_dict
from django.utils import timezone

from apps.api_vis.models import Clique, Commit, Entity, EntityProperty, Unification
from apps.api_vis.helpers import parse_project_version, validate_keys_and_types
from apps.exceptions import BadRequest, NotModified
from apps.files_management.models import Directory, File, FileVersion
from apps.projects.models import ProjectVersion


class DbHandler:
    def __init__(self, project_id, user):
        self.__project_id = project_id
        self.__user = user

    def get_all_cliques_in_project(self, qs_parameters):
        cliques = Clique.objects.filter(
            project_id=self.__project_id,
            created_in_commit__isnull=False,
        )

        if 'types' in qs_parameters:
            cliques = cliques.filter(type__in=qs_parameters['types'])

        if 'users' in qs_parameters:
            cliques = cliques.filter(created_by_id__in=qs_parameters['users'])

        if 'start_date' in qs_parameters:
            cliques = cliques.filter(unifications__created_on__gte=qs_parameters['start_date'])

        cliques = cliques.filter(deleted_in_commit__isnull=True)

        cliques = cliques.distinct().order_by('id')

        serialized_cliques = []

        for clique in cliques:
            unifications = clique.unifications

            unifications = unifications.filter(deleted_in_commit__isnull=True)

            unifications = unifications.order_by('id')

            serialized_clique = model_to_dict(clique, fields=['id', 'name', 'type'])

            entities_ids = unifications.values_list('entity_id', flat=True)
            entities_ids = list(entities_ids)

            serialized_clique.update({'entities': entities_ids})
            serialized_cliques.append(serialized_clique)

        return serialized_cliques

    def create_clique(self, request_data):
        clique_name = self.__get_clique_name(request_data)

        request_entities = request_data.get('entities')
        clique_type = self.__get_clique_type(request_entities)

        clique = self.__create_clique(clique_name, clique_type)

        return clique.id, clique_name

    def __get_clique_type(self, request_entities):
        entity_type = None

        for entity in request_entities:
            try:
                entity = self.get_entity_from_int_or_dict(entity, self.__project_id)

            except BadRequest:
                continue

            else:
                entity_type = entity.type

        if entity_type:
            return entity_type

        else:
            raise BadRequest("Can't get entity type from provided entity ids")

    def delete_clique(self, clique_id, project_version_nr):
        try:
            clique = self.__get_clique_from_db(clique_id)

            if clique.deleted_in_commit is not None:
                raise NotModified(f"Clique with id: {clique_id} is already deleted")

            self.__mark_clique_to_delete(clique, project_version_nr)

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
        project_version = self.__get_project_version_from_db(project_version_nr)

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

    def __get_clique_from_db(self, clique_id):
        try:
            clique = Clique.objects.get(
                id=clique_id,
            )

        except Clique.DoesNotExist:
            raise BadRequest(f"Clique with id: {clique_id} doesn't exist in project with id: {self.__project_id}")

        return clique

    def __mark_clique_to_delete(self, clique, project_version_nr):
        delete_time = timezone.now()

        clique.deleted_by = self.__user
        clique.deleted_on = delete_time
        clique.save()

        self.__mark_unifications_to_delete(clique, project_version_nr, delete_time)

    def __mark_unifications_to_delete(self, clique, project_version_nr, delete_time):
        unifications = clique.unifications.filter(
            deleted_in_commit__isnull=True
        )

        project_version = self.__get_project_version_from_db(project_version_nr)

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
            entity = self.get_entity_from_int_or_dict(request_entity, self.__project_id)

            project_version_nr = request_data.get('project_version')
            project_version = self.__get_project_version_from_db(project_version_nr)

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

    def __create_clique(self, clique_name, clique_type):
        clique = Clique.objects.create(
            project_id=self.__project_id,
            name=clique_name,
            type=clique_type,
            created_by=self.__user,
        )

        return clique

    def __get_project_version_from_db(self, project_version_nr):
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

    def add_unification(self, clique_id, entity_id, project_version_nr):
        try:
            project_version = self.__get_project_version_from_db(project_version_nr)
            entity = self.get_entity_from_int_or_dict(entity_id, self.__project_id)

            file_version = FileVersion.objects.get(
                projectversion=project_version,
                file=entity.file
            )

            Unification.objects.create(
                project=project_version.project,
                entity=entity,
                clique_id=clique_id,
                created_by=self.__user,
                created_in_file_version=file_version
            )

            unification_status = {
                'status': 200,
                'message': 'OK'
            }

        except BadRequest as exception:
            unification_status = {
                'status': 400,
                'message': str(exception)
            }

        return unification_status

    def get_entity_from_int_or_dict(self, request_entity, project_id):
        if type(request_entity) == int:
            try:
                entity = Entity.objects.get(
                    id=request_entity,
                )

                return entity

            except Entity.DoesNotExist:
                raise BadRequest(f"Entity with id: {request_entity} doesn't exist in project with id: {project_id}.")

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
                    file__project_id=project_id,
                    file_id=file_id,
                    xml_id=xml_id,
                    # deleted_on__isnull=True
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
        cliques_to_create = Clique.objects.filter(
            project_id=self.__project_id,
            created_by=self.__user,
            created_in_commit__isnull=True,
        )

        unifications_to_add = Unification.objects.filter(
            project_id=self.__project_id,
            created_by=self.__user,
            created_in_commit__isnull=True
        )

        cliques_to_delete = Clique.objects.filter(
            project_id=self.__project_id,
            deleted_by=self.__user,
            created_in_commit__isnull=False,
            deleted_in_commit__isnull=True,
        )

        unifications_to_delete = Unification.objects.filter(
            project_id=self.__project_id,
            deleted_by=self.__user,
            created_in_commit__isnull=False,
            deleted_in_commit__isnull=True,
        )

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
