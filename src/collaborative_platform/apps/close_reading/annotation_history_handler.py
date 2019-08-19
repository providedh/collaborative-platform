from django.contrib.sites.shortcuts import get_current_site
from django.db import connection
from lxml import etree

from apps.files_management.models import FileVersion

from .models import AnnotationHistory


class NoVersionException(Exception):
    pass


class AnnotationHistoryHandler:
    def __init__(self, project_id, file_id):
        self.__project_id = project_id
        self.__file_id = file_id

        self.__last_file_version_nr = 0
        self.__base_file_node = None

        self.__history = []

    def get_history(self, version):
        self.update_history()

        if version > len(self.__history):
            raise NoVersionException("There is no version {0} for this file. Latest file version is {1}.".format(
                    version, self.__last_file_version_nr))
        else:
            history = self.__history[:version]

            return history

    def update_history(self):
        self.__history = self.__get_history_from_db()

        file_version = FileVersion.objects.filter(file_id=self.__file_id).order_by('-number')[0]
        self.__last_file_version_nr = file_version.number

        if len(self.__history) == self.__last_file_version_nr:
            return

        elif len(self.__history) < self.__last_file_version_nr:
            self.__append_missing_history_steps()
            self.__save_history_to_db()
            return

        else:
            raise Exception("Number of file versions in annotation history are greater than number of existing "
                            "file versions.")

    def __get_history_from_db(self):
        try:
            annotation_history = AnnotationHistory.objects.get(project_id=self.__project_id,
                                                               file_id=self.__file_id)

        except AnnotationHistory.DoesNotExist:
            self.__create_history_in_db(self.__project_id, self.__file_id)
            annotation_history = AnnotationHistory.objects.get(project_id=self.__project_id,
                                                               file_id=self.__file_id)

        return annotation_history.history

    def __create_history_in_db(self, project_id, file_id):
        history = AnnotationHistory(project_id=project_id, file_id=file_id, history=[])
        history.save()

    def __append_missing_history_steps(self):
        versions_metadata = self.__get_versions_metadata_from_db()

        first_missing_version = len(self.__history) + 1
        last_missing_version = self.__last_file_version_nr

        for version_nr in range(first_missing_version, last_missing_version + 1):
            version_metadata = versions_metadata[version_nr - 1]
            history_step = self.__create_history_step(version_nr, version_metadata)
            self.__history.append(history_step)

    def __get_versions_metadata_from_db(self):
        versions_metadata = []

        with connection.cursor() as cursor:
            query = """
                SELECT V.number, V.creation_date, U.email
                FROM public.auth_user AS U
                INNER JOIN public.files_management_fileversion AS V
                    ON U.id = V.created_by_id
                WHERE V.file_id = {0}
                ORDER BY V.number
            """.format(self.__file_id)

            cursor.execute(query)
            results = cursor.fetchall()

            for result in results:
                metadata = {
                    'version': result[0],
                    'created': result[1],
                    'author_email': result[2],
                }

                versions_metadata.append(metadata)

        return versions_metadata

    def __create_history_step(self, version, version_metadata):
        text = self.__get_file_text(version)
        uncertainties = self.__count_uncertainties(text)

        request = None
        site = get_current_site(request)

        history_step = {
            'version': version,
            'contributor': version_metadata['author_email'],
            'timestamp': str(version_metadata['created']),
            'url': 'https://' + site.domain + '/files/' + str(self.__file_id) + '/version/' + str(version) + '/',
            'credibility': uncertainties['credibility'],
            'ignorance': uncertainties['ignorance'],
            'imprecision': uncertainties['imprecision'],
            'incompleteness': uncertainties['incompleteness'],
            'variation': uncertainties['variation'],
        }

        return history_step

    def __get_file_text(self, version):
        file_version = FileVersion.objects.get(file_id=self.__file_id, number=version)

        with open(file_version.upload.path) as file_version:
            text = file_version.read()

        return text

    def __count_uncertainties(self, text):
        text = self.__remove_encoding_line(text)
        tree = etree.fromstring(text)

        namespaces = {
            'default': "http://www.tei-c.org/ns/1.0",
        }

        uncertainties = {
            'credibility': 0,
            'ignorance': 0,
            'imprecision': 0,
            'incompleteness': 0,
            'variation': 0,
        }

        for key, value in uncertainties.items():
            number_of_uncertainties = len(
                tree.xpath("//default:classCode[@scheme=\"http://providedh.eu/uncertainty/ns/1.0\"]/"
                           "default:certainty[@source='" + key + "']", namespaces=namespaces))

            uncertainties[key] = number_of_uncertainties

        return uncertainties

    def __remove_encoding_line(self, text):
        text_in_lines = text.splitlines()
        first_line = text_in_lines[0]

        if "encoding=" in first_line:
            text_to_parse = text_in_lines[1:]
            text_to_parse = "\n".join(text_to_parse)

        else:
            text_to_parse = text

        return text_to_parse

    def __save_history_to_db(self):
        annotation_history = AnnotationHistory.objects.get(project_id=self.__project_id, file_id=self.__file_id)
        annotation_history.history = self.__history
        annotation_history.save()
