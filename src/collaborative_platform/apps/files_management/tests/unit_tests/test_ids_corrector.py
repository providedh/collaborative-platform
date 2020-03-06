import os
from apps.files_management.file_conversions.ids_corrector import IDsCorrector
from apps.projects.models import EntitySchema


DIRNAME = os.path.dirname(__file__)


class TestIDsCorrector:
    def test_correct_ids__correct_listable_entities__string(self, monkeypatch):
        monkeypatch.setattr(IDsCorrector, 'get_entities_schemes_from_db', fake_get_entities_schemes_from_db)
        monkeypatch.setattr(IDsCorrector, 'correct_collision_xml_ids', do_nothing)
        monkeypatch.setattr(IDsCorrector, 'correct_unlistable_entities_ids', do_nothing)
        monkeypatch.setattr(IDsCorrector, 'correct_custom_entities_ids', do_nothing)
        monkeypatch.setattr(IDsCorrector, 'correct_tags_ids_in_body_text_related_to_entities', do_nothing)

        source_file_path = os.path.join(DIRNAME, 'test_files', 'source_files', 'ids_filler_test_file.xml')
        expected_file_path = os.path.join(DIRNAME, 'test_files', 'expected_files',
                                          'correct_ids__correct_listable_entities.xml')

        source_xml = read_file(source_file_path)
        expected_xml = read_file(expected_file_path)

        project_id = 1

        ids_corrector = IDsCorrector()

        result_xml = ids_corrector.correct_ids(source_xml, project_id)

        assert result_xml == expected_xml

    def test_correct_ids__correct_unlistable_entities__string(self, monkeypatch):
        monkeypatch.setattr(IDsCorrector, 'get_entities_schemes_from_db', fake_get_entities_schemes_from_db)
        monkeypatch.setattr(IDsCorrector, 'correct_collision_xml_ids', do_nothing)
        monkeypatch.setattr(IDsCorrector, 'correct_listable_entities_ids', do_nothing)
        monkeypatch.setattr(IDsCorrector, 'correct_custom_entities_ids', do_nothing)
        monkeypatch.setattr(IDsCorrector, 'correct_tags_ids_in_body_text_related_to_entities', do_nothing)

        source_file_path = os.path.join(DIRNAME, 'test_files', 'source_files', 'ids_filler_test_file.xml')
        expected_file_path = os.path.join(DIRNAME, 'test_files', 'expected_files',
                                          'correct_ids__correct_unlistable_entities.xml')

        source_xml = read_file(source_file_path)
        expected_xml = read_file(expected_file_path)

        project_id = 1

        ids_corrector = IDsCorrector()

        result_xml = ids_corrector.correct_ids(source_xml, project_id)

        assert result_xml == expected_xml

    def test_correct_ids__correct_custom_entities__string(self, monkeypatch):
        monkeypatch.setattr(IDsCorrector, 'get_entities_schemes_from_db', fake_get_entities_schemes_from_db)
        monkeypatch.setattr(IDsCorrector, 'correct_collision_xml_ids', do_nothing)
        monkeypatch.setattr(IDsCorrector, 'correct_listable_entities_ids', do_nothing)
        monkeypatch.setattr(IDsCorrector, 'correct_unlistable_entities_ids', do_nothing)
        monkeypatch.setattr(IDsCorrector, 'correct_tags_ids_in_body_text_related_to_entities', do_nothing)

        source_file_path = os.path.join(DIRNAME, 'test_files', 'source_files', 'ids_filler_test_file.xml')
        expected_file_path = os.path.join(DIRNAME, 'test_files', 'expected_files',
                                          'correct_ids__correct_custom_entities.xml')

        source_xml = read_file(source_file_path)
        expected_xml = read_file(expected_file_path)

        project_id = 1

        ids_corrector = IDsCorrector()

        result_xml = ids_corrector.correct_ids(source_xml, project_id)

        assert result_xml == expected_xml

    def test_correct_ids__correct_collision_xml_ids__string(self, monkeypatch):
        monkeypatch.setattr(IDsCorrector, 'get_entities_schemes_from_db', fake_get_entities_schemes_from_db)
        monkeypatch.setattr(IDsCorrector, 'correct_listable_entities_ids', do_nothing)
        monkeypatch.setattr(IDsCorrector, 'correct_unlistable_entities_ids', do_nothing)
        monkeypatch.setattr(IDsCorrector, 'correct_custom_entities_ids', do_nothing)
        monkeypatch.setattr(IDsCorrector, 'correct_tags_ids_in_body_text_related_to_entities', do_nothing)

        source_file_path = os.path.join(DIRNAME, 'test_files', 'source_files', 'ids_filler_test_file.xml')
        expected_file_path = os.path.join(DIRNAME, 'test_files', 'expected_files',
                                          'correct_ids__correct_conflictual_xml_ids.xml')

        source_xml = read_file(source_file_path)
        expected_xml = read_file(expected_file_path)

        project_id = 1

        ids_correcor = IDsCorrector()

        result_xml = ids_correcor.correct_ids(source_xml, project_id)

        assert result_xml == expected_xml

    def test_correct_ids__correct_tags_ids_in_body_related_to_entities__string(self, monkeypatch):
        monkeypatch.setattr(IDsCorrector, 'get_entities_schemes_from_db', fake_get_entities_schemes_from_db)
        monkeypatch.setattr(IDsCorrector, 'correct_collision_xml_ids', do_nothing)
        monkeypatch.setattr(IDsCorrector, 'correct_listable_entities_ids', do_nothing)
        monkeypatch.setattr(IDsCorrector, 'correct_unlistable_entities_ids', do_nothing)
        monkeypatch.setattr(IDsCorrector, 'correct_custom_entities_ids', do_nothing)

        source_file_path = os.path.join(DIRNAME, 'test_files', 'source_files', 'ids_filler_test_file.xml')
        expected_file_path = os.path.join(DIRNAME, 'test_files', 'expected_files',
                                          'correct_ids__correct_tags_ids_in_body_related_to_entities.xml')

        source_xml = read_file(source_file_path)
        expected_xml = read_file(expected_file_path)

        project_id = 1

        ids_corrector = IDsCorrector()

        result_xml = ids_corrector.correct_ids(source_xml, project_id)

        assert result_xml == expected_xml


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
