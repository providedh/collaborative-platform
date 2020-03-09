import os
import pytest

from apps.files_management.file_conversions.ids_corrector import IDsCorrector
from apps.projects.models import EntitySchema


DIRNAME = os.path.dirname(__file__)


class TestIDsCorrector:
    def test_correct_ids__correct_listable_entities_ids__string(self, monkeypatch):
        monkeypatch.setattr(IDsCorrector, '_get_entities_schemes_from_db', fake_get_entities_schemes_from_db)
        monkeypatch.setattr(IDsCorrector, '_dump_max_xml_ids_to_db', do_nothing)

        source_file_path = os.path.join(DIRNAME, 'test_files', 'source_files',
                                        'correct_ids__correct_listable_entities_ids__source.xml')
        expected_file_path = os.path.join(DIRNAME, 'test_files', 'expected_files',
                                          'correct_ids__correct_listable_entities_ids__expected.xml')

        source_xml = read_file(source_file_path)
        expected_xml = read_file(expected_file_path)

        file_id = 1

        ids_corrector = IDsCorrector()
        result_xml, _ = ids_corrector.correct_ids(source_xml, file_id)

        assert result_xml == expected_xml

    def test_correct_ids__correct_unlistable_entities_ids__string(self, monkeypatch):
        monkeypatch.setattr(IDsCorrector, '_get_entities_schemes_from_db', fake_get_entities_schemes_from_db)
        monkeypatch.setattr(IDsCorrector, '_dump_max_xml_ids_to_db', do_nothing)

        source_file_path = os.path.join(DIRNAME, 'test_files', 'source_files',
                                        'correct_ids__correct_unlistable_entities_ids__source.xml')
        expected_file_path = os.path.join(DIRNAME, 'test_files', 'expected_files',
                                          'correct_ids__correct_unlistable_entities_ids__expected.xml')

        source_xml = read_file(source_file_path)
        expected_xml = read_file(expected_file_path)

        file_id = 1

        ids_corrector = IDsCorrector()
        result_xml, _ = ids_corrector.correct_ids(source_xml, file_id)

        assert result_xml == expected_xml

    def test_correct_ids__correct_custom_entities_ids__string(self, monkeypatch):
        monkeypatch.setattr(IDsCorrector, '_get_entities_schemes_from_db', fake_get_entities_schemes_from_db)
        monkeypatch.setattr(IDsCorrector, '_dump_max_xml_ids_to_db', do_nothing)

        source_file_path = os.path.join(DIRNAME, 'test_files', 'source_files',
                                        'correct_ids__correct_custom_entities_ids__source.xml')
        expected_file_path = os.path.join(DIRNAME, 'test_files', 'expected_files',
                                          'correct_ids__correct_custom_entities_ids__expected.xml')

        source_xml = read_file(source_file_path)
        expected_xml = read_file(expected_file_path)

        file_id = 1

        ids_corrector = IDsCorrector()
        result_xml, _ = ids_corrector.correct_ids(source_xml, file_id)

        assert result_xml == expected_xml

    def test_correct_ids__correct_collision_xml_ids__string(self, monkeypatch):
        monkeypatch.setattr(IDsCorrector, '_get_entities_schemes_from_db', fake_get_entities_schemes_from_db)
        monkeypatch.setattr(IDsCorrector, '_dump_max_xml_ids_to_db', do_nothing)

        source_file_path = os.path.join(DIRNAME, 'test_files', 'source_files',
                                        'correct_ids__correct_collision_xml_ids__source.xml')
        expected_file_path = os.path.join(DIRNAME, 'test_files', 'expected_files',
                                          'correct_ids__correct_collision_xml_ids__expected.xml')

        source_xml = read_file(source_file_path)
        expected_xml = read_file(expected_file_path)

        file_id = 1

        ids_correcor = IDsCorrector()
        result_xml, _ = ids_correcor.correct_ids(source_xml, file_id)

        assert result_xml == expected_xml

    def test_correct_ids__correct_tags_ids_in_body_related_to_entities__string(self, monkeypatch):
        monkeypatch.setattr(IDsCorrector, '_get_entities_schemes_from_db', fake_get_entities_schemes_from_db)
        monkeypatch.setattr(IDsCorrector, '_dump_max_xml_ids_to_db', do_nothing)

        source_file_path = os.path.join(DIRNAME, 'test_files', 'source_files',
                                        'correct_ids__correct_tags_ids_in_body_related_to_entities__source.xml')
        expected_file_path = os.path.join(DIRNAME, 'test_files', 'expected_files',
                                          'correct_ids__correct_tags_ids_in_body_related_to_entities__expected.xml')

        source_xml = read_file(source_file_path)
        expected_xml = read_file(expected_file_path)

        file_id = 1

        ids_corrector = IDsCorrector()
        result_xml, _ = ids_corrector.correct_ids(source_xml, file_id)

        assert result_xml == expected_xml

    def test_correct_ids__correct_certainties_ids__string(self, monkeypatch):
        monkeypatch.setattr(IDsCorrector, '_get_entities_schemes_from_db', fake_get_entities_schemes_from_db)
        monkeypatch.setattr(IDsCorrector, '_dump_max_xml_ids_to_db', do_nothing)

        source_file_path = os.path.join(DIRNAME, 'test_files', 'source_files',
                                        'correct_ids__correct_certainties_ids__source.xml')
        expected_file_path = os.path.join(DIRNAME, 'test_files', 'expected_files',
                                          'correct_ids__correct_certainties_ids__expected.xml')

        source_xml = read_file(source_file_path)
        expected_xml = read_file(expected_file_path)

        file_id = 1

        ids_corrector = IDsCorrector()
        result_xml, _ = ids_corrector.correct_ids(source_xml, file_id)

        assert result_xml == expected_xml

    def test_correct_ids__correct_all__string(self, monkeypatch):
        monkeypatch.setattr(IDsCorrector, '_get_entities_schemes_from_db', fake_get_entities_schemes_from_db)
        monkeypatch.setattr(IDsCorrector, '_dump_max_xml_ids_to_db', do_nothing)

        source_file_path = os.path.join(DIRNAME, 'test_files', 'source_files',
                                        'correct_ids__correct_all__source.xml')
        expected_file_path = os.path.join(DIRNAME, 'test_files', 'expected_files',
                                          'correct_ids__correct_all__expected.xml')

        source_xml = read_file(source_file_path)
        expected_xml = read_file(expected_file_path)

        file_id = 1

        ids_corrector = IDsCorrector()
        result_xml, _ = ids_corrector.correct_ids(source_xml, file_id)

        assert result_xml == expected_xml

    test_parameters_names = "source_file_name, expected"
    test_parameters_list = [
        ('correct_ids__correct_all__source.xml', True),
        ('correct_ids__is_correction__false__source.xml', False),
    ]

    @pytest.mark.parametrize(test_parameters_names, test_parameters_list)
    def test_correct_ids__is_correction__bool(self, monkeypatch, source_file_name, expected):
        monkeypatch.setattr(IDsCorrector, '_get_entities_schemes_from_db', fake_get_entities_schemes_from_db)
        monkeypatch.setattr(IDsCorrector, '_dump_max_xml_ids_to_db', do_nothing)

        source_file_path = os.path.join(DIRNAME, 'test_files', 'source_files', source_file_name)
        expected_file_path = os.path.join(DIRNAME, 'test_files', 'source_files', source_file_name)

        source_xml = read_file(source_file_path)
        expected_xml = read_file(expected_file_path)

        file_id = 1

        ids_corrector = IDsCorrector()
        result_xml, correction = ids_corrector.correct_ids(source_xml, file_id)

        if not expected:
            assert result_xml == expected_xml

        assert correction == expected


def read_file(path):
    with open(path, 'r') as file:
        text = file.read()

    return text


def do_nothing(*args, **kwargs):
    pass


def fake_get_entities_schemes_from_db(*args, **kwargs):
    entities = [
        EntitySchema(name='person'),
        EntitySchema(name='event'),
        EntitySchema(name='place'),
        EntitySchema(name='date'),
        EntitySchema(name='time'),
        EntitySchema(name='ingredient'),
    ]

    return entities
