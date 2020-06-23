from apps.api_vis.models import Clique, Entity, Unification
from apps.api_vis.helpers import parse_project_version, validate_keys_and_types
from apps.exceptions import BadRequest
from apps.files_management.models import Directory, File, FileVersion
from apps.projects.models import ProjectVersion



class DbHandler:
    def __init__(self, project_id, user):
        self.__project_id = project_id
        self.__user = user

    def create_clique(self, request_data):
        clique_name = self.__get_clique_name(request_data)

        clique = self.__create_clique(clique_name)

        return clique.id, clique_name

    @staticmethod
    def __get_clique_name(request_data):
        clique_name = request_data.get('name')

        return clique_name

    def __create_clique(self, clique_name):
        clique = Clique.objects.create(
            project_id=self.__project_id,
            asserted_name=clique_name,
            created_by=self.__user,
        )

        return clique

    def __get_project_version(self, project_version_nr):
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
            project_version = self.__get_project_version(project_version_nr)
            entity = self.get_entity_from_int_or_dict(entity_id, self.__project_id)

            file_version = FileVersion.objects.get(
                projectversion=project_version,
                file=entity.file
            )

            unification = Unification.objects.create(
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

            file_id = self.get_file_id_from_path(project_id, file_path)

            try:
                entity = Entity.objects.get(
                    project_id=project_id,
                    file_id=file_id,
                    xml_id=xml_id,
                    deleted_on__isnull=True
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