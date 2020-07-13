from copy import deepcopy

from django.db.models import Q
from django.utils import timezone

from apps.api_vis.models import Clique, Commit, Entity, EntityVersion, Unification
from apps.api_vis.helpers import parse_project_version
from apps.api_vis.request_validator import validate_keys_and_types
from apps.exceptions import BadRequest, NotModified
from apps.files_management.models import Directory, File, FileVersion
from apps.projects.models import ProjectVersion


class DbHandler:
    def __init__(self, project_id, user):
        self.__project_id = project_id
        self.__user = user

    def get_filtered_cliques(self, request_data, file_id=None):
        cliques = Clique.objects.filter(
            project_id=self.__project_id,
            created_in_commit__isnull=False,
        )

        if file_id:
            cliques = cliques.filter(
                unifications__entity__file_id=file_id,
            )

        if 'types' in request_data:
            cliques = cliques.filter(type__in=request_data['types'])

        if 'users' in request_data:
            cliques = cliques.filter(created_by_id__in=request_data['users'])

        if 'start_date' in request_data:
            cliques = cliques.filter(unifications__created_on__gte=request_data['start_date'])

        if 'end_date' in request_data:
            cliques = cliques.filter(unifications__created_on__lte=request_data['end_date'])

        if 'project_version' in request_data or 'date' in request_data:
            project_version_nr = request_data.get('project_version')
            date = request_data.get('date')

            project_version = self.get_project_version(project_version_nr, date)
            commit = project_version.latest_commit

            cliques = cliques.filter(
                Q(unifications__deleted_in_commit_id__gte=commit.id) | Q(unifications__deleted_in_commit__isnull=True),
                unifications__created_in_commit_id__lte=commit.id,
            )

        else:
            cliques = cliques.filter(deleted_in_commit__isnull=True)

        cliques = cliques.distinct().order_by('id')

        return cliques

    def get_filtered_unifications(self, request_data, clique=None):
        if clique:
            unifications = clique.unifications

        else:
            unifications = Unification.objects.filter(
                project_id=self.__project_id,
                created_in_commit__isnull=False,
            )

        if 'users' in request_data:
            unifications = unifications.filter(created_by_id__in=request_data['users'])

        if 'start_date' in request_data:
            unifications = unifications.filter(created_on__gte=request_data['start_date'])

        if 'end_date' in request_data:
            unifications = unifications.filter(created_on__lte=request_data['end_date'])

        if 'project_version' in request_data or 'date' in request_data:
            project_version_nr = request_data.get('project_version')
            date = request_data.get('date')

            project_version = self.get_project_version(project_version_nr, date)
            commit = project_version.latest_commit

            unifications = unifications.filter(
                Q(deleted_in_commit_id__gte=commit.id) | Q(deleted_in_commit_id__isnull=True),
                created_in_commit_id__lte=commit.id,
            )

        else:
            unifications = unifications.filter(deleted_in_commit__isnull=True)

        unifications = unifications.order_by('id')

        return unifications

    def get_filtered_entities(self, request_data, file_id=None):
        entities = Entity.objects.filter(
            file__project_id=self.__project_id,
            created_in_file_version__isnull=False,
        )

        if file_id:
            entities = entities.filter(file_id=file_id)

        if 'types' in request_data:
            entities = entities.filter(type__in=request_data['types'])

        if 'users' in request_data:
            entities = entities.filter(created_by_id__in=request_data['users'])

        if 'project_version' in request_data or 'date' in request_data:
            project_version_nr = request_data.get('project_version')
            date = request_data.get('date')

            project_version = self.get_project_version(project_version_nr, date)
            file_versions_ids = project_version.file_versions.values_list('id', flat=True)

            entities = entities.filter(
                versions__file_version_id__in=file_versions_ids
            )

        else:
            entities = entities.filter(deleted_in_file_version__isnull=True)

        entities = entities.order_by('id')

        return entities

    def get_filtered_unbound_entities(self, request_data, file_id=None):
        parameters_for_entities = deepcopy(request_data)
        parameters_for_entities.pop('users', None)

        entities = self.get_filtered_entities(parameters_for_entities, file_id)
        unifications = self.get_filtered_unifications(request_data)

        bound_entities_ids = []

        for unification in unifications:
            bound_entities_ids.append(unification.entity.id)

        bound_entities_ids = set(bound_entities_ids)

        entities = entities.exclude(id__in=bound_entities_ids)

        return entities

    def create_clique(self, clique_name, clique_type):
        clique = Clique.objects.create(
            project_id=self.__project_id,
            name=clique_name,
            type=clique_type,
            created_by=self.__user,
        )

        return clique

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

    def create_commit(self, message):
        cliques_to_create = self.get_cliques_to_create()
        unifications_to_add = self.get_unifications_to_create()
        cliques_to_delete = self.get_cliques_to_delete()
        unifications_to_delete = self.get_unifications_to_delete()

        if len(cliques_to_create) + len(unifications_to_add) + len(cliques_to_delete) + \
                len(unifications_to_delete) == 0:
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

    def delete_clique(self, clique, project_version):
        clique.deleted_by = self.__user
        clique.deleted_on = timezone.now()
        clique.save()

        unifications = clique.unifications.filter(
            deleted_in_commit__isnull=True
        )

        self.__delete_unifications(unifications, project_version)

    def delete_unification(self, unification, project_version, save=True):
        file_version = project_version.file_versions.get(
            file=unification.entity.file
        )

        unification.deleted_by = self.__user
        unification.deleted_on = timezone.now()
        unification.deleted_in_file_version = file_version

        if save:
            unification.save()

    def get_clique(self, clique_id):
        try:
            clique = Clique.objects.get(
                id=clique_id,
            )

        except Clique.DoesNotExist:
            raise BadRequest(f"Clique with id: {clique_id} doesn't exist in project with id: {self.__project_id}")

        return clique

    @staticmethod
    def get_unification(clique, entity):
        try:
            unification = Unification.objects.get(
                clique=clique,
                entity=entity
            )

        except Unification.DoesNotExist:
            raise BadRequest(f"Clique with id: {clique.id} doesn't contain entity with id: {entity.id}")

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

            file_id = self.__get_file_id_from_path(file_path)

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

    def get_entity_property(self, entity, project_version, property_name):
        entity_version = self.__get_entity_version(entity, project_version)

        property_version = entity_version.properties.get(
            name=property_name
        )

        return property_version

    def get_project_version(self, project_version_nr, date):
        if project_version_nr:
            project_version = self.get_project_version_by_nr(project_version_nr)

        elif date:
            project_version = self.get_project_version_by_date(date)

        else:
            project_version = self.get_project_version_latest()

        return project_version

    def get_project_version_by_nr(self, project_version_nr):
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

    def get_project_version_by_date(self, date):
        project_version = ProjectVersion.objects.filter(
            project_id=self.__project_id,
            date__lte=date,
        ).latest('id')

        if not project_version:
            raise BadRequest(f"There is no version of project with id: {self.__project_id} for date: "
                             f"{date.isoformat()}")

        return project_version

    def get_project_version_latest(self):
        project_version = ProjectVersion.objects.filter(
            project_id=self.__project_id,
        ).latest('id')

        return project_version

    def get_cliques_to_create(self):
        cliques_to_create = Clique.objects.filter(
            project_id=self.__project_id,
            created_by=self.__user,
            created_in_commit__isnull=True,
        )

        return cliques_to_create

    def get_unifications_to_create(self):
        unifications_to_add = Unification.objects.filter(
            project_id=self.__project_id,
            created_by=self.__user,
            created_in_commit__isnull=True
        )

        return unifications_to_add

    def get_cliques_to_delete(self):
        cliques_to_delete = Clique.objects.filter(
            project_id=self.__project_id,
            deleted_by=self.__user,
            created_in_commit__isnull=False,
            deleted_in_commit__isnull=True,
        )

        return cliques_to_delete

    def get_unifications_to_delete(self):
        unifications_to_delete = Unification.objects.filter(
            project_id=self.__project_id,
            deleted_by=self.__user,
            created_in_commit__isnull=False,
            deleted_in_commit__isnull=True,
        )

        return unifications_to_delete

    @staticmethod
    def __get_entity_version(entity, project_version):
        file_version = project_version.file_versions.get(
            file=entity.file
        )

        entity_version = EntityVersion.objects.get(
            entity=entity,
            file_version=file_version
        )

        return entity_version

    def __get_file_id_from_path(self, file_path, parent_directory_id=None):
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

                return self.__get_file_id_from_path(rest_of_path, directory.id)

            except Directory.DoesNotExist:
                raise BadRequest(f"Directory with name {directory_name} does't exist in this directory.")

    def __delete_unifications(self, unifications, project_version):
        for unification in unifications:
            self.delete_unification(unification, project_version, save=False)

        Unification.objects.bulk_update(unifications, ['deleted_by', 'deleted_on', 'deleted_in_file_version'])
