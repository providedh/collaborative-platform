import os
import pytest
import time

from django.conf import settings
from django.contrib.auth.models import User
from django.test import Client

from apps.files_management.models import Directory, File
from apps.projects.models import Project


SCRIPT_DIR = os.path.dirname(__file__)


@pytest.fixture(scope='class')
def prepare_media_directory(tmp_path_factory):
    media_directory = tmp_path_factory.mktemp('media', numbered=False)
    settings.MEDIA_ROOT = media_directory

    uploaded_files_dir = media_directory / 'uploaded_files'
    uploaded_files_dir.mkdir()


@pytest.mark.usefixtures('prepare_media_directory')
@pytest.mark.django_db(transaction=True)
@pytest.mark.integration_tests
class TestFileUploadWithHdAndDb:
    def test_file_upload_create_file_on_hd_and_entries_in_db(self):
        user_id = 2
        project_id = 1

        client = Client()
        user = User.objects.get(id=user_id)
        client.force_login(user)

        files_in_db = File.objects.all()
        assert len(files_in_db) == 0

        files_on_hd = os.listdir(os.path.join(settings.MEDIA_ROOT, 'uploaded_files'))
        assert len(files_on_hd) == 0

        project = Project.objects.get(id=project_id)
        directory = Directory.objects.get(project=project, name=project.title)
        file_name = 'group_0_long_original_0.xml'

        with open(os.path.join(SCRIPT_DIR, 'test_files', file_name)) as uploaded_file:
            client.post(f'/api/files/upload/{directory.id}/', {'name': file_name, 'file': uploaded_file})

        files_in_db = File.objects.all()
        assert len(files_in_db) == 1

        files_on_hd = os.listdir(os.path.join(settings.MEDIA_ROOT, 'uploaded_files'))
        assert len(files_on_hd) == 2
