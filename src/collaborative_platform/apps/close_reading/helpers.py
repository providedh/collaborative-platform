import xmltodict
import json

from lxml import etree

from apps.api_vis.models import Unification
from apps.files_management.models import File


def verify_reference(file_id, asserted_value):
    file = File.objects.get(id=file_id, deleted=False)
    path_to_file = file.get_relative_path()

    path_to_reference, person_id = asserted_value.split('#')

    if path_to_file == path_to_reference:
        asserted_value = '#' + person_id

    return asserted_value


def unification_xml_elements_to_json(unifications):
    unifications_to_return = []

    for unification in unifications:
        unification = etree.tostring(unification, encoding='utf-8')
        parsed_unification = xmltodict.parse(unification)

        del parsed_unification['certainty']['@xmlns']

        entity_xml_id = parsed_unification['certainty']['@target'][1:]
        xml_id_number = int(parsed_unification['certainty']['@xml:id'].split('-')[-1])

        unification__in_db = Unification.objects.get(
            entity__xml_id=entity_xml_id,
            xml_id_number=xml_id_number,
            deleted_on__isnull=True,
        )

        parsed_unification['committed'] = True if unification__in_db.created_in_commit else False

        unifications_to_return.append(parsed_unification)

    unifications_to_return = json.dumps(unifications_to_return)

    return unifications_to_return
