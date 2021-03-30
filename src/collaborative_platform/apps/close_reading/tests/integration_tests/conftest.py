import os
import pytest

from shutil import copytree, ignore_patterns, rmtree

from django.core.management import call_command

from collaborative_platform.settings_for_tests import MEDIA_ROOT


SCRIPT_DIR = os.path.dirname(__file__)


# TODO: Replace all fixtures creating databases from all `conftest.py` files with one file and fixture parametrization


@pytest.fixture(scope='function')
def annotator_with_ws_and_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        media_for_tests_dir = os.path.basename(MEDIA_ROOT)

        if 'media_for_tests' not in media_for_tests_dir:
            raise ValueError(f"You try to run tests with '{media_for_tests_dir}' catalogue instead 'media_for_tests' "
                             f"catalogue. Check if you use 'settings_for_tests' module in your 'pytest.ini' file.")

        path_to_fixture = os.path.join(SCRIPT_DIR, 'database_fixture', 'annotator_tests_db_fixture.json')
        call_command('loaddata', path_to_fixture)

        __create_db_files_directory()

        yield

        call_command('flush', '--no-input')

        __remove_db_files_directory()


@pytest.fixture(scope='function')
def reset_db_files_directory_before_each_test():
    __remove_db_files_directory()
    __create_db_files_directory()


def __create_db_files_directory():
    source_files = os.path.join(SCRIPT_DIR, 'database_fixture', 'media')

    copytree(source_files, MEDIA_ROOT, ignore=ignore_patterns('.keep'))


def __remove_db_files_directory():
    rmtree(MEDIA_ROOT)
