import copy
import hashlib
import json
import re
import xmltodict

from io import BytesIO
from json import loads
from lxml import etree
from typing import List, Set

from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.files.uploadedfile import UploadedFile
from django.db.models import Q
from django.forms import model_to_dict
from django.http import JsonResponse
from django.utils import timezone

import apps.index_and_search.models as es

from apps.api_vis.models import Clique, Unification, Certainty
from apps.close_reading.annotator import NAMESPACES
from apps.files_management.file_conversions.xml_formatter import XMLFormatter
from apps.files_management.models import File, FileVersion, Directory, FileMaxXmlIds
from apps.index_and_search.content_extractor import ContentExtractor
from apps.index_and_search.entities_extractor import EntitiesExtractor
from apps.index_and_search.models import Person, Organization, Event, Place, Ingredient, Utensil, ProductionMethod
from apps.projects.helpers import log_activity
from apps.projects.models import Project

ALL_ES_ENTITIES = (Person, Organization, Event, Place, Ingredient, Utensil, ProductionMethod, es.File)


def upload_file(uploaded_file, project, user, parent_dir=None):  # type: (UploadedFile, Project, User, int) -> File
    # I assume that the project exists, bc few level above we checked if user has permissions to write to it.

    try:
        File.objects.get(name=uploaded_file.name, parent_dir_id=parent_dir, project=project, deleted=False)
    except File.DoesNotExist:
        dbfile = File(name=uploaded_file.name, parent_dir_id=parent_dir, project=project, version_number=1)
        dbfile.save()

        try:
            hash = hash_file(dbfile, uploaded_file)
            uploaded_file.name = hash
            file_version = FileVersion(upload=uploaded_file, number=1, hash=hash, file=dbfile, created_by=user)
            file_version.save()
            FileMaxXmlIds(file=dbfile).save()
        except Exception as e:
            dbfile.delete()
            raise e
        else:
            log_activity(project, user, "created", file=dbfile)
            return dbfile
    else:
        raise Exception(f"File with name {uploaded_file.name} already exist in this directory")


def overwrite_file(dbfile, uploaded_file, user):  # type: (File, UploadedFile, User) -> File
    hash = hash_file(dbfile, uploaded_file)
    latest_file_version = dbfile.versions.filter(number=dbfile.version_number).get()  # type: FileVersion
    if latest_file_version.hash == hash:
        return dbfile  # current file is the same as uploaded one

    uploaded_file.name = hash
    new_version_number = latest_file_version.number + 1
    new_file_version = FileVersion(upload=uploaded_file, number=new_version_number, hash=hash, file=dbfile,
                                   created_by=user, creation_date=timezone.now())

    dbfile.version_number = new_version_number
    dbfile.save()

    try:
        new_file_version.save()
    except:
        dbfile.version_number -= 1
        dbfile.save()

    log_activity(dbfile.project, user, action_text="created version number {} of".format(new_version_number),
                 file=dbfile)
    return dbfile


def hash_file(dbfile, uploaded_file):  # type: (File, UploadedFile) -> str
    uploaded_file.seek(0)
    hashed = bytes(uploaded_file.name, encoding='utf8') + \
             bytes(str(dbfile.project_id), encoding='utf8') + \
             bytes(str(dbfile.parent_dir_id), encoding='utf8') + \
             uploaded_file.read()
    hash = hashlib.sha512(hashed).hexdigest()
    return hash


def create_uploaded_file_object_from_string(string, file_name):  # type: (str, str) -> UploadedFile
    file = BytesIO(string.encode('utf-8'))

    uploaded_file = UploadedFile(file=file, name=file_name)

    return uploaded_file


def extract_text_and_entities(contents, project_id, file_id):  # type: (str, int, int) -> (str, List[dict])
    if len(contents) == 0:
        return "", []
    text = ContentExtractor.tei_contents_to_text(contents)
    entities = EntitiesExtractor.extract_entities(contents)
    entities = EntitiesExtractor.extend_entities(entities, project_id, file_id)
    return text, entities


def index_entities(entities):  # type: (List[dict]) -> None
    classes = {
        'person': Person,
        'org': Organization,
        'event': Event,
        'place': Place,
        'ingredient': Ingredient,
        'utensil': Utensil,
        'productionMethod': ProductionMethod
    }

    for entity in copy.deepcopy(entities):
        if entity['tag'] not in classes:
            continue

        tag = entity.pop('tag')

        # make sure we're not passing excessive keyword arguments to constructor, as that would cause an error
        tag_elements = {f[0] for f in classes[tag]._ObjectBase__list_fields()}
        excessive_elements = set(entity.keys()).difference(tag_elements)
        tuple(map(entity.pop, excessive_elements))  # pop all excessive elements from entity

        es_entity = classes[tag](**entity)
        es_entity.save()


def get_directory_content(dir, indent):  # type: (Directory, int) -> dict
    files = list(map(model_to_dict, dir.files.filter(deleted=False)))
    for file in files:
        file['kind'] = 'file'
        file['icon'] = 'fa-file-xml-o'
        file['open'] = False
        file['parent'] = dir.id
        file['indent'] = indent + 1

    subdirs = [get_directory_content(subdir, indent + 1) for subdir in dir.subdirs.filter(deleted=False)]

    result = model_to_dict(dir)
    result['parent'] = dir.parent_dir_id or 0
    result['children'] = files + subdirs
    result['kind'] = "folder"
    result['icon'] = 'fa-file-folder-o'
    result['open'] = not indent
    result['show'] = not indent
    result['indent'] = indent

    return result


def get_all_child_dirs(directory):  # type: (Directory) -> Set[int]
    children = set()

    for child in directory.subdirs.all():
        children.add(child.id)
        children.update(get_all_child_dirs(child))

    return children


def is_child(parent, child):  # type: (int, int) -> bool
    parent_dir = Directory.objects.get(id=parent, deleted=False)
    children = get_all_child_dirs(parent_dir)
    return child in children


def include_user(response):  # type: (JsonResponse) -> JsonResponse
    json = loads(response.content)
    for fv in json['data']:
        u = User.objects.get(id=fv['created_by_id'])  # type: User
        fv['created_by'] = u.first_name + ' ' + u.last_name

    return JsonResponse(json)


def delete_es_docs(file_id):  # type: (int) -> None
    for entity_model in ALL_ES_ENTITIES:
        entity_model.search().filter('term', file_id=file_id).delete()


def index_file(dbfile, text):  # type: (File, str) -> None
    es.File(name=dbfile.name,
            id=dbfile.id,
            _id=dbfile.id,
            project_id=dbfile.project.id,
            text=text
            ).save()


def delete_directory_with_contents_fake(directory_id, user):  # type: (int, User) -> None
    child_directories = Directory.objects.filter(parent_dir=directory_id, deleted=False)

    for directory in child_directories:
        delete_directory_with_contents_fake(directory_id=directory.id, user=user)

    files = File.objects.filter(parent_dir=directory_id, deleted=False)

    for file in files:
        file.delete_fake(user)
        log_activity(project=file.project, user=user, action_text=f"deleted file {file.name}")

    directory = Directory.objects.get(id=directory_id)
    directory.delete_fake()
    log_activity(project=directory.project, user=user, related_dir=directory,
                 action_text=f"deleted directory {directory.name}")


def append_unifications(xml_content, file_version):  # type: (str, FileVersion) -> str
    certainty_elements = create_certainty_elements_for_file_version(file_version)

    if certainty_elements:
        xml_in_lines = xml_content.splitlines()
        if 'encoding=' in xml_in_lines[0]:
            xml_content = '\n'.join(xml_in_lines[1:])

        xml_tree = etree.fromstring(xml_content)

        add_certainties_to_xml_tree(certainty_elements, xml_tree)
        fill_up_certainty_authors_list(xml_tree)

        xml_content = etree.tounicode(xml_tree)
        xml_formatter = XMLFormatter()

        if xml_formatter.check_if_reformat_is_needed(xml_content):
            xml_content = xml_formatter.reformat_xml(xml_content)

    return xml_content


def create_certainty_elements_for_file_version(file_version, include_uncommitted=False, user=None, for_annotator=False):
    # type: (FileVersion, bool, User, bool) -> list

    if include_uncommitted and not user:
        raise ValueError("Argument 'include_uncommitted' require to fill a 'user' argument.")

    if for_annotator and not include_uncommitted:
        raise ValueError("Argument 'for_annotator' require to set a 'include_uncommitted' argument to 'True'.")

    cliques = Clique.objects.filter(
        Q(unifications__deleted_in_file_version__isnull=True)
        | Q(unifications__deleted_in_file_version__number__gte=file_version.number),
        unifications__created_in_file_version__number__lte=file_version.number,
        project_id=file_version.file.project_id,
        unifications__entity__file=file_version.file,
    ).distinct()

    if include_uncommitted and for_annotator:
        cliques = cliques.filter(
            (Q(created_in_commit__isnull=True) & Q(created_in_annotator=False) & Q(created_by=user))
            | (Q(created_in_commit__isnull=True) & Q(created_in_annotator=True))
            | Q(created_in_commit__isnull=False)
        )
    elif include_uncommitted and not for_annotator:
        cliques = cliques.filter(
            (Q(created_in_commit__isnull=True) & Q(created_by=user))
            | Q(created_in_commit__isnull=False),
        )
    else:
        cliques = cliques.filter(
            created_in_commit__isnull=False,
        )

    certainty_elements_to_add = []

    for clique in cliques:
        unifications = Unification.objects.filter(
            clique=clique,
            deleted_on__isnull=True,
        )

        if include_uncommitted and for_annotator:
            unifications = unifications.filter(
                (Q(created_in_commit__isnull=True) & Q(created_in_annotator=False) & Q(created_by=user))
                | (Q(created_in_commit__isnull=True) & Q(created_in_annotator=True))
                | Q(created_in_commit__isnull=False)
            )
        elif include_uncommitted and not for_annotator:
            unifications = unifications.filter(
                (Q(created_in_commit__isnull=True) & Q(created_by=user))
                | Q(created_in_commit__isnull=False),
            )
        else:
            unifications = unifications.filter(
                created_in_commit__isnull=False,
            )

        internal_unifications = unifications.filter(
            entity__file=file_version.file,
        )

        external_unifications = unifications.filter(
            ~Q(entity__file=file_version.file),
        )

        unification_elements = create_certainty_elements_from_unifications(internal_unifications, external_unifications)
        certainty_elements_to_add.extend(unification_elements)

        certainties = Certainty.objects.filter(
            unification__in=unifications,
        )

        certainty_elements = create_certainty_elements_from_certainties(certainties)
        certainty_elements_to_add.extend(certainty_elements)

    return certainty_elements_to_add


def create_certainty_elements_from_unifications(internal_unifications, external_unifications):
    # type: (list, list) -> list
    external_unification_xml_ids = [unification.entity.file.get_path() + '#' + unification.entity.xml_id
                                    for unification in external_unifications]

    certainties = []

    for unification in internal_unifications:
        default_namespace = NAMESPACES['default']
        xml_namespace = NAMESPACES['xml']
        default = '{%s}' % default_namespace
        xml = '{%s}' % xml_namespace

        ns_map = {
            None: default_namespace,
            'xml': xml_namespace,
        }

        ana = ''
        locus = 'value'
        certainty = unification.certainty
        annotator_id = '#person' + str(unification.created_by_id)

        entity_xml_id = unification.entity.xml_id
        target = '#' + entity_xml_id

        internal_unification_xml_ids = ['#' + unification.entity.xml_id for unification in internal_unifications if
                                        unification.entity.xml_id != entity_xml_id]
        asserted_value = ' '.join(internal_unification_xml_ids + external_unification_xml_ids)

        certainty = etree.Element(default + 'certainty', ana=ana, locus=locus, cert=certainty,
                                  resp=annotator_id, target=target, match='@sameAs', assertedValue=asserted_value,
                                  nsmap=ns_map)

        certainty_xml_id = unification.xml_id
        certainty.attrib[etree.QName(xml + 'id')] = certainty_xml_id

        certainties.append(certainty)

    return certainties


def create_certainty_elements_from_certainties(certainties):
    certainties_to_return = []

    for certainty in certainties:
        default_namespace = NAMESPACES['default']
        xml_namespace = NAMESPACES['xml']
        default = '{%s}' % default_namespace
        xml = '{%s}' % xml_namespace

        ns_map = {
            None: default_namespace,
            'xml': xml_namespace,
        }

        certainty_element = etree.Element(
            default + 'certainty',
            ana=certainty.ana,
            locus=certainty.locus,
            cert=certainty.cert,
            resp=certainty.resp,
            target='#' + certainty.target,
            match='@sameAs',
            nsmap=ns_map)

        certainty_element.attrib[etree.QName(xml + 'id')] = certainty.xml_id

        if certainty.asserted_value:
            certainty_element.attrib['assertedValue'] = certainty.asserted_value

        if certainty.description:
            description = etree.Element('desc', nsmap=ns_map)
            description.text = certainty.description

            certainty_element.append(description)

        certainties_to_return.append(certainty_element)

    return certainties_to_return


def certainty_elements_to_json(unifications):
    unifications_to_return = []

    for unification in unifications:
        unification = etree.tostring(unification, encoding='utf-8')
        parsed_unification = xmltodict.parse(unification)

        del parsed_unification['certainty']['@xmlns']

        entity_xml_id = parsed_unification['certainty']['@target'][1:]
        xml_id = parsed_unification['certainty']['@xml:id']
        target_type = entity_xml_id.split('_')[0]

        unification_in_db = Unification.objects.get(
            xml_id=entity_xml_id if target_type == 'certainty' else xml_id,
            deleted_on__isnull=True,
        )

        parsed_unification['committed'] = True if unification_in_db.created_in_commit else False

        unifications_to_return.append(parsed_unification)

    unifications_to_return = json.dumps(unifications_to_return)

    return unifications_to_return


def add_certainties_to_xml_tree(certainty_elements, xml_tree):
    certainties_node = xml_tree.xpath('//default:teiHeader'
                                      '//default:classCode[@scheme="http://providedh.eu/uncertainty/ns/1.0"]',
                                      namespaces=NAMESPACES)

    if not certainties_node:
        xml_tree = create_annotation_list(xml_tree)
        certainties_node = xml_tree.xpath('//default:teiHeader'
                                          '//default:classCode[@scheme="http://providedh.eu/uncertainty/ns/1.0"]',
                                          namespaces=NAMESPACES)

    for certainty in certainty_elements:
        xpath = f'//default:teiHeader' \
                f'//default:classCode[@scheme="http://providedh.eu/uncertainty/ns/1.0"]' \
                f'//default:certainty[@ana="{certainty.attrib["ana"]}" ' \
                f'and @locus="{certainty.attrib["locus"]}" ' \
                f'and @cert="{certainty.attrib["cert"]}" ' \
                f'and @target="{certainty.attrib["target"]}"'

        if 'assertedValue' in certainty.attrib:
            xpath += f' and @assertedValue="{certainty.attrib["assertedValue"]}"'

        xpath += ']'

        existing_certainties = xml_tree.xpath(xpath, namespaces=NAMESPACES)

        desc = certainty.xpath('.//desc', namespaces=NAMESPACES)

        if not existing_certainties:
            certainties_node[0].append(certainty)

        else:
            for existing_certainty in existing_certainties:
                existing_desc = existing_certainty.xpath('.//desc', namespaces=NAMESPACES)

                if desc and existing_desc:
                    if desc.text() != existing_desc.text():
                        certainties_node[0].append(certainty)
                elif desc:
                    certainties_node[0].append(certainty)


def create_annotation_list(tree):
    default_namespace = NAMESPACES['default']
    default = "{%s}" % default_namespace

    ns_map = {
        None: default_namespace
    }

    profile_desc = tree.xpath('//default:teiHeader/default:profileDesc', namespaces=NAMESPACES)

    if not profile_desc:
        tei_header = tree.xpath('//default:teiHeader', namespaces=NAMESPACES)
        profile_desc = etree.Element(default + 'profileDesc', nsmap=ns_map)
        tei_header[0].append(profile_desc)

    text_class = tree.xpath('//default:teiHeader/default:profileDesc/default:textClass', namespaces=NAMESPACES)

    if not text_class:
        profile_desc = tree.xpath('//default:teiHeader/default:profileDesc', namespaces=NAMESPACES)
        text_class = etree.Element(default + 'textClass', nsmap=ns_map)
        profile_desc[0].append(text_class)

    class_code = tree.xpath(
        '//default:teiHeader/default:profileDesc/default:textClass/default:classCode[@scheme="http://providedh.eu/uncertainty/ns/1.0"]',
        namespaces=NAMESPACES)

    if not class_code:
        text_class = tree.xpath('//default:teiHeader/default:profileDesc/default:textClass', namespaces=NAMESPACES)
        class_code = etree.Element(default + 'classCode', scheme="http://providedh.eu/uncertainty/ns/1.0",
                                   nsmap=ns_map)
        text_class[0].append(class_code)

    return tree


def fill_up_certainty_authors_list(xml_tree):
    list_person = xml_tree.xpath('//default:teiHeader'
                                 '//default:listPerson[@type="PROVIDEDH Annotators"]', namespaces=NAMESPACES)

    if not list_person:
        xml_tree = create_list_person(xml_tree)
        list_person = xml_tree.xpath('//default:teiHeader'
                                     '//default:listPerson[@type="PROVIDEDH Annotators"]', namespaces=NAMESPACES)

    certainty_authors = xml_tree.xpath('//default:teiHeader'
                                       '//default:classCode[@scheme="http://providedh.eu/uncertainty/ns/1.0"]'
                                       '//default:certainty/@resp',
                                       namespaces=NAMESPACES)
    certainty_authors = set(certainty_authors)

    for author in certainty_authors:
        author = author.replace('#', '')
        author_in_list = list_person[0].xpath(f'./default:person[@xml:id="{author}"]', namespaces=NAMESPACES)

        if not author_in_list:
            author_element = create_author_element(author)
            list_person[0].append(author_element)

    return xml_tree


def create_list_person(xml_tree):
    prefix = "{%s}" % NAMESPACES['default']

    ns_map = {
        None: NAMESPACES['default']
    }

    profile_desc = xml_tree.xpath('//default:teiHeader/default:profileDesc', namespaces=NAMESPACES)

    if not profile_desc:
        tei_header = xml_tree.xpath('//default:teiHeader', namespaces=NAMESPACES)
        profile_desc = etree.Element(prefix + 'profileDesc', nsmap=ns_map)
        tei_header[0].append(profile_desc)

    partic_desc = xml_tree.xpath('//default:teiHeader/default:profileDesc/default:particDesc', namespaces=NAMESPACES)

    if not partic_desc:
        profile_desc = xml_tree.xpath('//default:teiHeader/default:profileDesc', namespaces=NAMESPACES)
        partic_desc = etree.Element(prefix + 'particDesc', nsmap=ns_map)
        profile_desc[0].append(partic_desc)

    list_person = xml_tree.xpath(
        '//default:teiHeader/default:profileDesc/default:particDesc/default:listPerson[@type="PROVIDEDH Annotators"]',
        namespaces=NAMESPACES)

    if not list_person:
        partic_desc = xml_tree.xpath('//default:teiHeader/default:profileDesc/default:particDesc',
                                     namespaces=NAMESPACES)
        list_person = etree.Element(prefix + 'listPerson', type="PROVIDEDH Annotators", nsmap=ns_map)
        partic_desc[0].append(list_person)

    return xml_tree


def create_author_element(author):  # type: (str) -> etree.Element
    user_id = author.replace('person', '')
    user_id = int(user_id)

    user = User.objects.get(id=user_id)

    request = None
    site = get_current_site(request)

    annotator = f"""
                <person xml:id="{author}">
                  <persName>
                    <forename>{user.first_name}</forename>
                    <surname>{user.last_name}</surname>
                    <email>{user.email}</email>
                  </persName>
                  <link>https://{site.domain}/user/{user_id}/</link>
                </person>
            """

    annotator_xml = etree.fromstring(annotator)

    return annotator_xml


def clean_name(name):
    name = re.sub(r'[^a-zA-Z0-9\-_]', '_', name)

    return name
