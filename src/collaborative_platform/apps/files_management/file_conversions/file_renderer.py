from lxml import etree

from django.contrib.auth.models import User
from django.db.models import Q

from apps.files_management.file_conversions.xml_tools import add_property_to_element, get_or_create_element_from_xpath
from apps.api_vis.models import Certainty, EntityProperty, EntityVersion, Unification
from apps.projects.models import EntitySchema

from collaborative_platform.settings import XML_NAMESPACES, DEFAULT_ENTITIES, NS_MAP, CUSTOM_ENTITY


class FileRenderer:
    def __init__(self):
        self.__file_version = None

        self.__tree = None

        self.__listable_entities = []
        self.__custom_entities = []

    def render_file_version(self, file_version):
        self.__file_version = file_version

        self.__load_entities_schemes()

        self.__create_tree()
        self.__append_listable_entities()
        self.__append_custom_entities()
        self.__append_certainties()
        self.__append_unifications()
        self.__append_annotators()

        # TODO: Fix appending unifications

        # TODO: Reorder lists in <body>

        # TODO: Move appending line with xml-model here

        xml_content = self.__create_xml_content()

        return xml_content

    def __create_tree(self):
        raw_content = self.__file_version.get_raw_content()

        parser = etree.XMLParser(remove_blank_text=True)
        self.__tree = etree.fromstring(raw_content, parser=parser)

    def __load_entities_schemes(self):
        entities_schemes = self.__get_entities_schemes_from_db()

        default_entities_names = DEFAULT_ENTITIES.keys()

        for entity in entities_schemes:
            if entity.name not in default_entities_names:
                self.__custom_entities.append(entity)
            elif DEFAULT_ENTITIES[entity.name]['listable']:
                self.__listable_entities.append(entity)

    def __get_entities_schemes_from_db(self):
        entities_schemes = EntitySchema.objects.filter(taxonomy__project=self.__file_version.file.project).order_by('id')

        return entities_schemes

    def __append_listable_entities(self):
        for entity in self.__listable_entities:
            entities_versions = self.__get_entities_versions_from_db(entity.name)

            if entities_versions:
                elements = self.__create_entities_elements(entities_versions)

                list_tag = DEFAULT_ENTITIES[entity.name]['list_tag']

                if entity.body_list:
                    list_xpath = f'./default:text/default:body/default:div[@type="{entity.name}"]/' \
                                 f'default:{list_tag}[@type="{entity.name}List"]'
                else:
                    list_xpath = f'./default:teiHeader/default:fileDesc/default:sourceDesc/' \
                                 f'default:{list_tag}[@type="{entity.name}List"]'

                self.__append_elements_to_the_list(elements, list_xpath)

    def __append_custom_entities(self):
        for entity in self.__custom_entities:
            entities_versions = self.__get_entities_versions_from_db(entity.name)

            if entities_versions:
                elements = self.__create_entities_elements(entities_versions, custom=True)

                if entity.body_list:
                    list_xpath = f'./default:text/default:body/default:div[@type="{entity.name}"]/' \
                                 f'default:listObject[@type="{entity.name}List"]'
                else:
                    list_xpath = f'./default:teiHeader/default:fileDesc/default:sourceDesc/' \
                                 f'default:listObject[@type="{entity.name}List"]'

                self.__append_elements_to_the_list(elements, list_xpath)

    def __get_entities_versions_from_db(self, entity_type):
        entities_versions = EntityVersion.objects.filter(
            file_version=self.__file_version,
            entity__type=entity_type,
        )

        return entities_versions

    def __create_entities_elements(self, entities_versions, custom=False):
        elements = []

        for entity_version in entities_versions:
            entity_element = self.__create_entity_element(entity_version, custom)

            self.__append_entity_properties(entity_element, entity_version, custom)

            elements.append(entity_element)

        return elements

    @staticmethod
    def __create_entity_element(entity_version, custom=False):
        default_prefix = '{%s}' % XML_NAMESPACES['default']
        xml_prefix = '{%s}' % XML_NAMESPACES['xml']

        if not custom:
            entity_element = etree.Element(default_prefix + entity_version.entity.type, nsmap=NS_MAP)
        else:
            entity_element = etree.Element(default_prefix + 'object', nsmap=NS_MAP)
            entity_element.set('type', entity_version.entity.type)

        entity_element.set(xml_prefix + 'id', entity_version.entity.xml_id)
        entity_element.set('resp', f'#annotator-{entity_version.entity.created_by_id}')

        return entity_element

    @staticmethod
    def __append_entity_properties(entity_element, entity_version, custom=False):
        entities_properties = EntityProperty.objects.filter(
            entity_version=entity_version
        ).order_by('name')

        if not custom:
            properties = DEFAULT_ENTITIES[entity_version.entity.type]['properties']
        else:
            properties = CUSTOM_ENTITY['properties']

        for entity_property in entities_properties:
            xpath = properties[entity_property.name]['xpath']
            value = entity_property.get_value(as_str=True)

            add_property_to_element(entity_element, xpath, value)

    def __append_elements_to_the_list(self, elements, list_xpath):
        list = get_or_create_element_from_xpath(self.__tree, list_xpath, XML_NAMESPACES)

        for element in elements:
            list.append(element)

    def __create_xml_content(self):
        xml_content = etree.tounicode(self.__tree, pretty_print=True)

        return xml_content

    def __append_certainties(self):
        certainties = self.__get_certainties_from_db().order_by('id')

        if certainties:
            elements = self.__create_certainties_elements(certainties)

            list_xpath = './default:teiHeader/default:profileDesc/default:textClass/' \
                         'default:classCode[@scheme="http://providedh.eu/uncertainty/ns/1.0"]'

            self.__append_elements_to_the_list(elements, list_xpath)

    def __get_certainties_from_db(self):
        certainties = Certainty.objects.filter(
            file_version=self.__file_version
        )

        return certainties

    def __create_certainties_elements(self, certainties):
        elements = []

        for certainty in certainties:
            certainty_element = self.__create_certainty_element(certainty)

            elements.append(certainty_element)

        return elements

    @staticmethod
    def __create_certainty_element(certainty):
        default_prefix = '{%s}' % XML_NAMESPACES['default']
        xml_prefix = '{%s}' % XML_NAMESPACES['xml']

        certainty_element = etree.Element(default_prefix + 'certainty', nsmap=NS_MAP)

        certainty_element.set(xml_prefix + 'id', certainty.xml_id)
        certainty_element.set('resp', f'#annotator-{certainty.created_by_id}')

        certainty_element.set('ana', certainty.get_categories(as_str=True))
        certainty_element.set('locus', certainty.locus)
        certainty_element.set('cert', certainty.certainty)

        # TODO: Keep `target` attribute in database in form `#<xml:id-X.0> #<xml:id-X.1>` from the beginning
        # TODO: to avoid appending `#` on every request

        target = certainty.target_xml_id
        targets = target.split(' ')
        targets = [f'#{xml_id}' for xml_id in targets]
        target = ' '.join(targets)
        certainty_element.set('target', target)

        if certainty.degree:
            certainty_element.set('degree', str(certainty.degree))

        if certainty.target_match:
            certainty_element.set('match', certainty.target_match)

        if certainty.asserted_value:
            certainty_element.set('assertedValue', certainty.asserted_value)

        if certainty.description:
            description_element = etree.Element(default_prefix + 'desc', nsmap=NS_MAP)
            description_element.text = certainty.description

            certainty_element.append(description_element)

        return certainty_element

    def __append_unifications(self):
        unifications = self.__get_unifications_from_db().order_by('id')
        certainties = self.__convert_unifications_to_certainties(unifications)

    def __get_unifications_from_db(self):
        unifications = Unification.objects.filter(
            Q(deleted_in_file_version__number__gte=self.__file_version.number)
            | Q(deleted_in_file_version__isnull=True),
            created_in_file_version__number__lte=self.__file_version.number,
            created_in_file_version__file=self.__file_version.file,
        )

        return unifications

    def __convert_unifications_to_certainties(self, unifications):
        certainties = []

        for unification in unifications:
            certainty = Certainty()

        return certainties

    def __append_annotators(self):
        users_ids = self.__get_annotators_ids_of_xml_elements()
        users = self.__get_users_from_db(users_ids)

        if users:
            elements = self.__create_annotators_elements(users)

            list_xpath = './default:teiHeader/default:profileDesc/default:particDesc/' \
                         'default:listPerson[@type="PROVIDEDH Annotators"]'

            self.__append_elements_to_the_list(elements, list_xpath)

    def __get_annotators_ids_of_xml_elements(self):
        xpath = '//@resp'
        annotators = self.__tree.xpath(xpath, namespaces=XML_NAMESPACES)
        annotators = set(annotators)

        annotators_ids = [int(annotator.replace('#annotator-', '')) for annotator in annotators]

        return annotators_ids

    @staticmethod
    def __get_users_from_db(users_ids):
        users = User.objects.filter(id__in=users_ids)

        return users

    def __create_annotators_elements(self, annotators):
        elements = []

        for annotator in annotators:
            annotator_element = self.__create_annotator_element(annotator)

            elements.append(annotator_element)

        return elements

    @staticmethod
    def __create_annotator_element(annotator):
        default_prefix = '{%s}' % XML_NAMESPACES['default']
        xml_prefix = '{%s}' % XML_NAMESPACES['xml']

        annotator_element = etree.Element(default_prefix + 'person', nsmap=NS_MAP)
        annotator_element.set(xml_prefix + 'id', f'annotator-{annotator.id}')

        forename_xpath = './default:persName/default:forename'
        forename_element = get_or_create_element_from_xpath(annotator_element, forename_xpath, XML_NAMESPACES)
        forename_element.text = annotator.first_name

        surname_xpath = './default:persName/default:surname'
        surname_element = get_or_create_element_from_xpath(annotator_element, surname_xpath, XML_NAMESPACES)
        surname_element.text = annotator.last_name

        email_xpath = './default:persName/default:email'
        email_element = get_or_create_element_from_xpath(annotator_element, email_xpath, XML_NAMESPACES)
        email_element.text = annotator.email

        return annotator_element
