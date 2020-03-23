import os
import pytest

from shutil import copytree, ignore_patterns, rmtree

from django.conf import settings
from django.core.management import call_command


SCRIPT_DIR = os.path.dirname(__file__)


@pytest.fixture(scope='class')
def test_file_upload_with_hd_and_db__db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        media_for_tests_dir = settings.MEDIA_ROOT.split()[-1]

        if 'media_for_tests' not in media_for_tests_dir:
            raise ValueError(f"You try to run tests with '{media_for_tests_dir}' catalogue instead 'media_for_tests' "
                             f"catalogue. Check if you use 'settings_for_tests' module in your 'pytest.ini' file.")

        path_to_fixture = os.path.join(SCRIPT_DIR, 'database_fixture', 'file_upload_tests_db_fixture.json')
        call_command('loaddata', path_to_fixture)

        source_files = os.path.join(SCRIPT_DIR, 'database_fixture', 'media')
        copytree(source_files, settings.MEDIA_ROOT, ignore=ignore_patterns('.keep'))

        yield

        call_command('flush', '--no-input')

        rmtree(settings.MEDIA_ROOT)
