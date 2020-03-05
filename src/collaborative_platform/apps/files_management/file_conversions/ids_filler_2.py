from lxml import etree

from django.conf import settings

from apps.projects.models import EntitySchema


class IDsFiller:
    def __init__(self):
        self.namespaces = settings.XML_NAMESPACES
        self.xml_id_key = f"{{{self.namespaces['xml']}}}id"

        self.tree = None

        self.listable_entities = []
        self.unlistable_entities = []
        self.custom_entities = []

        self.max_xml_ids = {}

    def correct_ids(self, xml_content, project_id):
        self.load_entities_schemes(project_id)
        self.initiate_max_xml_ids()

        self.create_tree(xml_content)
        self.correct_listable_entities_ids()
        self.correct_unlistable_entities_ids()
        self.correct_custom_entities_ids()

        xml_content = self.create_xml_content()

        return xml_content

    def load_entities_schemes(self, project_id):
        entities_schemes = self.get_entities_schemes_from_db(project_id)

        default_entities_names = settings.ENTITIES.keys()

        for entity in entities_schemes:
            if entity.name not in default_entities_names:
                self.custom_entities.append(entity)
            else:
                if settings.ENTITIES[entity.name]['listable']:
                    self.listable_entities.append(entity)
                else:
                    self.unlistable_entities.append(entity)

    @staticmethod
    def get_entities_schemes_from_db(project_id):
        entities_schemes = EntitySchema.objects.filter(taxonomy__project_id=project_id)

        return entities_schemes

    def initiate_max_xml_ids(self):
        entities = self.listable_entities + self.unlistable_entities + self.custom_entities

        for entity in entities:
            self.max_xml_ids.update({entity.name: 0})

    def create_tree(self, xml_content):
        parser = etree.XMLParser(remove_blank_text=True)

        self.tree = etree.fromstring(xml_content, parser=parser)

    def correct_listable_entities_ids(self):
        for entity in self.listable_entities:
            list_tag = settings.ENTITIES[entity.name]['list_tag']
            xpath = f'//default:{list_tag}[@type="{entity.name}List"]//default:{entity.name}'

            self.correct_entities_ids(xpath, entity.name)

    def correct_unlistable_entities_ids(self):
        for entity in self.unlistable_entities:
            xpath = f'//default:text//default:body//default:{entity.name}'

            self.correct_entities_ids(xpath, entity.name)

    def correct_custom_entities_ids(self):
        for entity in self.custom_entities:
            xpath = f'//default:listObject[@type="{entity.name}List"]//default:object[@type="{entity.name}"]'

            self.correct_entities_ids(xpath, entity.name)

    def correct_entities_ids(self, xpath, entity_name):
        elements = self.tree.xpath(xpath, namespaces=self.namespaces)

        for element in elements:
            if self.xml_id_key in element.attrib:
                self.update_element_xml_id_and_refs(element, entity_name)

            else:
                self.update_element_xml_id(element, entity_name)

    def update_element_xml_id_and_refs(self, element, entity_name):
        old_xml_id = element.attrib[self.xml_id_key]
        new_xml_id = self.update_element_xml_id(element, entity_name)

        xpath = f"//*[contains(concat(' ', @ref, ' '), ' #{old_xml_id} ')]"

        elements = self.tree.xpath(xpath, namespaces=self.namespaces)

        for element in elements:
            self.update_element_ref(element, old_xml_id, new_xml_id)

    def update_element_xml_id(self, element, entity_name):
        xml_id_number = self.get_next_xml_id_number(entity_name)
        new_xml_id = f'{entity_name}-{xml_id_number}'

        element.attrib[self.xml_id_key] = new_xml_id

        return new_xml_id

    def update_element_ref(self, element, old_xml_id, new_xml_id):
        old_ref = element.attrib['ref']
        new_ref = old_ref.replace(f'#{old_xml_id}', f'#{new_xml_id}')
        element.attrib['ref'] = new_ref

    def get_next_xml_id_number(self, entity_name):
        xml_id_number = self.max_xml_ids[entity_name]

        self.max_xml_ids[entity_name] += 1

        return xml_id_number

    def create_xml_content(self):
        xml_content = etree.tounicode(self.tree, pretty_print=True)

        return xml_content
