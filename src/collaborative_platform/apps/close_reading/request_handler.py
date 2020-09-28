from apps.close_reading.enums import ElementTypes
from apps.close_reading.db_handler import DbHandler
from apps.close_reading.response_generator import get_listable_entities_types
from apps.close_reading.xml_handler import XmlHandler
from apps.exceptions import BadRequest, Forbidden, UnsavedElement


class RequestHandler:
    def __init__(self, user, file_id):
        self.__db_handler = DbHandler(user, file_id)
        self.__operations_results = []

        annotator_xml_id = self.__db_handler.get_annotator_xml_id()
        self.__xml_handler = XmlHandler(annotator_xml_id)

        file = self.__db_handler.get_file_from_db(file_id)
        self.__listable_entities_types = get_listable_entities_types(file.project)

    def modify_file(self, operations):
        self.__clean_operation_results()

        for operation in operations:
            element_saved = True

            if operation['element_type'] == 'tag':
                if operation['method'] == 'POST':
                    self.__add_tag(operation)
                elif operation['method'] == 'PUT':
                    element_saved = self.__move_tag(operation)
                elif operation['method'] == 'DELETE':
                    self.__delete_tag(operation)
                else:
                    raise BadRequest("There is no operation matching to this request")

            elif operation['element_type'] == 'reference':
                if operation['method'] == 'POST':
                    self.__add_reference_to_entity(operation)
                elif operation['method'] == 'PUT':
                    element_saved = self.__modify_reference_to_entity(operation)
                elif operation['method'] == 'DELETE':
                    self.__delete_reference_to_entity(operation)
                else:
                    raise BadRequest("There is no operation matching to this request")

            elif operation['element_type'] == 'entity_property':
                if operation['method'] == 'POST':
                    self.__add_entity_property(operation)
                elif operation['method'] == 'PUT':
                    element_saved = self.__modify_entity_property(operation)
                elif operation['method'] == 'DELETE':
                    self.__delete_entity_property(operation)
                else:
                    raise BadRequest("There is no operation matching to this request")

            elif operation['element_type'] == 'certainty':
                if operation['method'] == 'POST':
                    self.__add_certainty(operation)
                elif operation['method'] == 'PUT':
                    element_saved = self.__modify_certainty(operation)
                elif operation['method'] == 'DELETE':
                    self.__delete_certainty(operation)
                else:
                    raise BadRequest("There is no operation matching to this request")

            else:
                raise BadRequest(f"There is no operation matching to this request")

            operation_result = self.__operations_results[-1]
            dependencies_ids = []

            if element_saved:
                if operation['method'] == 'POST':
                    dependencies_ids = self.__find_dependencies(operation, operation_result)

                self.__db_handler.add_operation(operation, operation_result, dependencies_ids)
            else:
                if operation['method'] == 'PUT':
                    dependencies_ids = self.__find_dependencies(operation, operation_result, modification=True)

                self.__db_handler.update_operation(operation, operation_result, dependencies_ids)

    def discard_changes(self, operations_ids):
        operations = self.__db_handler.get_operations(operations_ids, with_dependent=True, from_latest=True)

        for operation in operations:
            if operation['element_type'] == 'tag':
                if operation['method'] == 'POST':
                    self.__discard_adding_tag(operation)
                elif operation['method'] == 'PUT':
                    self.__discard_moving_tag(operation)
                elif operation['method'] == 'DELETE':
                    self.__discard_deleting_tag(operation)

            elif operation['element_type'] == 'reference':
                if operation['method'] == 'POST':
                    self.__discard_adding_reference(operation)
                elif operation['method'] == 'PUT':
                    self.__discard_modifying_reference(operation)
                elif operation['method'] == 'DELETE':
                    self.__discard_removing_reference(operation)

            elif operation['element_type'] == 'entity_property':
                if operation['method'] == 'POST':
                    self.__discard_adding_entity_property(operation)
                elif operation['method'] == 'PUT':
                    self.__discard_modifying_entity_property(operation)
                elif operation['method'] == 'DELETE':
                    self.__discard_removing_entity_property(operation)

            elif operation['element_type'] == 'certainty':
                if operation['method'] == 'POST':
                    self.__discard_adding_certainty(operation)
                elif operation['method'] == 'PUT':
                    self.__discard_modifying_certainty(operation)
                elif operation['method'] == 'DELETE':
                    self.__discard_removing_certainty(operation)

            else:
                raise BadRequest("There is no operation matching to this request")

            operation_id = operation['id']
            self.__db_handler.delete_operation(operation_id)

    def save_changes(self, operations_ids):
        operations = self.__db_handler.get_operations(operations_ids)
        self.__verify_if_dependencies_will_be_saved(operations)
        new_file_version = self.__start_saving_file()

        for operation in operations:
            if operation['element_type'] == 'tag':
                if operation['method'] == 'POST':
                    self.__accept_adding_tag(operation)
                elif operation['method'] == 'PUT':
                    self.__accept_moving_tag(operation)
                elif operation['method'] == 'DELETE':
                    self.__accept_deleting_tag(operation)

            elif operation['element_type'] == 'reference':
                if operation['method'] == 'POST':
                    self.__accept_adding_reference(operation, new_file_version)
                elif operation['method'] == 'PUT':
                    self.__accept_modifying_reference(operation, new_file_version)
                elif operation['method'] == 'DELETE':
                    self.__accept_removing_reference(operation, new_file_version)

            elif operation['element_type'] == 'entity_property':
                if operation['method'] == 'POST':
                    self.__accept_adding_entity_property(operation, new_file_version)
                elif operation['method'] == 'PUT':
                    self.__accept_modifying_entity_property(operation, new_file_version)
                elif operation['method'] == 'DELETE':
                    self.__accept_removing_entity_property(operation, new_file_version)

            elif operation['element_type'] == 'certainty':
                if operation['method'] == 'POST':
                    self.__accept_adding_certainty(operation, new_file_version)
                elif operation['method'] == 'PUT':
                    self.__accept_modifying_certainty(operation, new_file_version)
                elif operation['method'] == 'DELETE':
                    self.__accept_removing_certainty(operation, new_file_version)

            else:
                raise BadRequest("There is no operation matching to this request")

            operation_id = operation['id']
            self.__db_handler.delete_operation(operation_id)

        self.__finish_saving_file(new_file_version)

    def __add_tag(self, request):
        # TODO: Add verification if this same tag not existing already
        # TODO: Add possibility to add tag if text fragment is separated by another tag

        start_pos = request['parameters']['start_pos']
        end_pos = request['parameters']['end_pos']
        tag_xml_id = self.__db_handler.get_next_xml_id('ab')

        body_content = self.__db_handler.get_body_content()
        body_content = self.__xml_handler.add_tag(body_content, start_pos, end_pos, tag_xml_id)
        self.__db_handler.set_body_content(body_content)

        self.__operations_results.append(tag_xml_id)

    def __move_tag(self, request):
        new_start_pos = request['parameters']['start_pos']
        new_end_pos = request['parameters']['end_pos']
        tag_xml_id = request['edited_element_id']

        body_content = self.__db_handler.get_body_content()

        try:
            self.__xml_handler.check_permissions(body_content, tag_xml_id)
            body_content, saved = self.__xml_handler.move_tag(body_content, new_start_pos, new_end_pos, tag_xml_id)

        except Forbidden:
            raise BadRequest("Modification of an element created by another user is forbidden.")

        self.__db_handler.set_body_content(body_content)

        self.__operations_results.append(tag_xml_id)

        return saved

    def __delete_tag(self, request):
        tag_xml_id = request['edited_element_id']

        body_content = self.__db_handler.get_body_content()

        try:
            self.__xml_handler.check_permissions(body_content, tag_xml_id)
            body_content = self.__xml_handler.delete_tag(body_content, tag_xml_id)

        except Forbidden:
            raise BadRequest("Removal of an element created by another user is forbidden.")

        except UnsavedElement:
            raise BadRequest("Deleting an unsaved element is forbidden. Instead of deleting, discard "
                             "the operation that created this element.")

        self.__db_handler.set_body_content(body_content)

        self.__operations_results.append(None)

    def __add_reference_to_entity(self, request):
        # TODO: Add verification if user has rights to edit a tag

        tag_xml_id = request['edited_element_id']
        tag_xml_id = self.__update_target_xml_id(tag_xml_id)

        if tag_xml_id != request['edited_element_id']:
            request['edited_element_id'] = tag_xml_id

        entity_xml_id = request.get('new_element_id')
        entity_xml_id = self.__update_target_xml_id(entity_xml_id)

        if 'new_element_id' in request and entity_xml_id != request['new_element_id']:
            request['new_element_id'] = entity_xml_id

        try:
            entity_type = request['parameters']['entity_type']
        except KeyError:
            entity_type = self.__db_handler.get_entity_type(entity_xml_id)

        if not entity_xml_id and entity_type in self.__listable_entities_types:
            entity_xml_id = self.__db_handler.add_entity(entity_type)

            new_tag = 'name'
            new_tag_xml_id = self.__db_handler.get_next_xml_id(new_tag)

            body_content = self.__db_handler.get_body_content()
            body_content = self.__xml_handler.add_reference_to_entity(body_content, tag_xml_id, new_tag, new_tag_xml_id,
                                                                      entity_xml_id)
            self.__db_handler.set_body_content(body_content)

        elif not entity_xml_id and entity_type not in self.__listable_entities_types:
            entity_xml_id = self.__db_handler.add_entity(entity_type)

            body_content = self.__db_handler.get_body_content()
            body_content = self.__xml_handler.add_reference_to_entity(body_content, tag_xml_id, entity_type,
                                                                      entity_xml_id, entity_xml_id)
            self.__db_handler.set_body_content(body_content)

        elif entity_xml_id and entity_type in self.__listable_entities_types:
            new_tag = 'name'
            new_tag_xml_id = self.__db_handler.get_next_xml_id(new_tag)

            body_content = self.__db_handler.get_body_content()
            body_content = self.__xml_handler.add_reference_to_entity(body_content, tag_xml_id, new_tag, new_tag_xml_id,
                                                                      entity_xml_id)
            self.__db_handler.set_body_content(body_content)

        elif entity_xml_id and entity_type not in self.__listable_entities_types:
            new_tag_xml_id = self.__db_handler.get_next_xml_id(entity_type)

            body_content = self.__db_handler.get_body_content()
            body_content = self.__xml_handler.add_reference_to_entity(body_content, tag_xml_id, entity_type,
                                                                      new_tag_xml_id, entity_xml_id)
            self.__db_handler.set_body_content(body_content)

        else:
            raise BadRequest("There is no operation matching to this request")

        self.__operations_results.append(entity_xml_id)

    def __modify_reference_to_entity(self, request):
        # TODO: Add verification if user has rights to edit a tag

        tag_xml_id = request['edited_element_id']
        old_entity_xml_id = request['old_element_id']
        new_entity_xml_id = request.get('new_element_id')

        try:
            new_entity_type = request['parameters']['entity_type']
        except KeyError:
            new_entity_type = self.__db_handler.get_entity_type(new_entity_xml_id)

        old_entity_type = self.__db_handler.get_entity_type(old_entity_xml_id)

        if not new_entity_xml_id and new_entity_type in self.__listable_entities_types:
            body_content = self.__db_handler.get_body_content()

            try:
                self.__xml_handler.check_permissions(body_content, tag_xml_id)

                new_entity_xml_id = self.__db_handler.add_entity(new_entity_type)

                new_tag = 'name'
                new_tag_xml_id = self.__get_new_tag_xml_id(tag_xml_id, new_tag)

                tag_is_an_entity = self.__xml_handler.check_if_tag_is_an_entity(body_content, tag_xml_id)
                body_content, saved = self.__xml_handler.modify_reference_to_entity(body_content, tag_xml_id,
                                                                                    new_entity_xml_id,
                                                                                    old_entity_xml_id,
                                                                                    new_tag, new_tag_xml_id)

                if old_entity_type not in self.__listable_entities_types and tag_is_an_entity:
                    old_entity_properties = self.__db_handler.get_entity_properties_values(old_entity_xml_id,
                                                                                           include_unsaved=True)

                    body_content = self.__xml_handler.delete_entity_properties(body_content, new_tag_xml_id,
                                                                               old_entity_properties)

                self.__db_handler.set_body_content(body_content)

                last_reference = self.__xml_handler.check_if_last_reference(body_content, old_entity_xml_id)

                if last_reference:
                    self.__db_handler.delete_entity(old_entity_xml_id)

            except Forbidden:
                raise BadRequest("Modification of an element created by another user is forbidden.")

        elif not new_entity_xml_id and new_entity_type not in self.__listable_entities_types:
            body_content = self.__db_handler.get_body_content()

            try:
                self.__xml_handler.check_permissions(body_content, tag_xml_id)

                new_entity_xml_id = self.__db_handler.add_entity(new_entity_type)

                tag_is_an_entity = self.__xml_handler.check_if_tag_is_an_entity(body_content, tag_xml_id)
                body_content, saved = self.__xml_handler.modify_reference_to_entity(body_content, tag_xml_id,
                                                                                    new_entity_xml_id,
                                                                                    old_entity_xml_id,
                                                                                    new_entity_type, new_entity_xml_id)

                if old_entity_type not in self.__listable_entities_types and tag_is_an_entity:
                    old_entity_properties = self.__db_handler.get_entity_properties_values(old_entity_xml_id,
                                                                                           include_unsaved=True)

                    body_content = self.__xml_handler.delete_entity_properties(body_content, new_entity_xml_id,
                                                                               old_entity_properties)

                self.__db_handler.set_body_content(body_content)

                last_reference = self.__xml_handler.check_if_last_reference(body_content, old_entity_xml_id)

                if last_reference:
                    self.__db_handler.delete_entity(old_entity_xml_id)

            except Forbidden:
                raise BadRequest("Modification of an element created by another user is forbidden.")

        elif new_entity_xml_id and new_entity_type in self.__listable_entities_types:
            body_content = self.__db_handler.get_body_content()

            try:
                self.__xml_handler.check_permissions(body_content, tag_xml_id)

                new_tag = 'name'
                new_tag_xml_id = self.__get_new_tag_xml_id(tag_xml_id, new_tag)

                tag_is_an_entity = self.__xml_handler.check_if_tag_is_an_entity(body_content, tag_xml_id)
                body_content, saved = self.__xml_handler.modify_reference_to_entity(body_content, tag_xml_id,
                                                                                    new_entity_xml_id,
                                                                                    old_entity_xml_id,
                                                                                    new_tag, new_tag_xml_id)

                if old_entity_type not in self.__listable_entities_types and tag_is_an_entity:
                    old_entity_properties = self.__db_handler.get_entity_properties_values(old_entity_xml_id,
                                                                                           include_unsaved=True)

                    body_content = self.__xml_handler.delete_entity_properties(body_content, new_tag_xml_id,
                                                                               old_entity_properties)

                self.__db_handler.set_body_content(body_content)

                last_reference = self.__xml_handler.check_if_last_reference(body_content, old_entity_xml_id)

                if last_reference:
                    self.__db_handler.delete_entity(old_entity_xml_id)

            except Forbidden:
                raise BadRequest("Modification of an element created by another user is forbidden.")

        elif new_entity_xml_id and new_entity_type not in self.__listable_entities_types:
            body_content = self.__db_handler.get_body_content()

            try:
                self.__xml_handler.check_permissions(body_content, tag_xml_id)

                new_tag_xml_id = self.__get_new_tag_xml_id(tag_xml_id, new_entity_type)

                tag_is_an_entity = self.__xml_handler.check_if_tag_is_an_entity(body_content, tag_xml_id)
                body_content, saved = self.__xml_handler.modify_reference_to_entity(body_content, tag_xml_id,
                                                                                    new_entity_xml_id,
                                                                                    old_entity_xml_id,
                                                                                    new_entity_type, new_tag_xml_id)

                if old_entity_type not in self.__listable_entities_types and tag_is_an_entity:
                    old_entity_properties = self.__db_handler.get_entity_properties_values(old_entity_xml_id,
                                                                                           include_unsaved=True)

                    body_content = self.__xml_handler.delete_entity_properties(body_content, tag_xml_id,
                                                                               old_entity_properties)

                self.__db_handler.set_body_content(body_content)

                last_reference = self.__xml_handler.check_if_last_reference(body_content, old_entity_xml_id)

                if last_reference:
                    self.__db_handler.delete_entity(old_entity_xml_id)

            except Forbidden:
                raise BadRequest("Modification of an element created by another user is forbidden.")

        else:
            raise BadRequest("There is no operation matching to this request")

        self.__operations_results.append(new_entity_xml_id)

        return saved

    def __delete_reference_to_entity(self, request):
        tag_xml_id = request.get('edited_element_id')
        entity_xml_id = request.get('old_element_id')

        new_tag = 'ab'
        new_tag_xml_id = self.__get_new_tag_xml_id(tag_xml_id, new_tag)

        entity_type = self.__db_handler.get_entity_type(entity_xml_id)

        if entity_type in self.__listable_entities_types:
            body_content = self.__db_handler.get_body_content()

            try:
                self.__xml_handler.check_permissions(body_content, tag_xml_id)

                body_content = self.__xml_handler.delete_reference_to_entity(body_content, tag_xml_id, new_tag,
                                                                             new_tag_xml_id, entity_xml_id)

                self.__db_handler.set_body_content(body_content)

                last_reference = self.__xml_handler.check_if_last_reference(body_content, entity_xml_id)

                if last_reference:
                    self.__db_handler.delete_entity(entity_xml_id)

            except Forbidden:
                raise BadRequest("Removal of an element created by another user is forbidden.")

            except UnsavedElement:
                raise BadRequest("Deleting an unsaved element is forbidden. Instead of deleting, discard "
                                 "the operation that created this element.")

        else:
            body_content = self.__db_handler.get_body_content()

            entity_properties_values = self.__db_handler.get_entity_properties_values(entity_xml_id)

            try:
                self.__xml_handler.check_permissions(body_content, tag_xml_id)

                body_content = self.__xml_handler.delete_reference_to_entity(body_content, tag_xml_id, new_tag,
                                                                             new_tag_xml_id, entity_xml_id)

                body_content = self.__xml_handler.delete_entity_properties(body_content, entity_xml_id,
                                                                           entity_properties_values)
                self.__db_handler.set_body_content(body_content)

                last_reference = self.__xml_handler.check_if_last_reference(body_content, entity_xml_id)

                if last_reference:
                    self.__db_handler.delete_entity(entity_xml_id)

            except Forbidden:
                raise BadRequest("Removal of an element created by another user is forbidden.")

            except UnsavedElement:
                raise BadRequest("Deleting an unsaved element is forbidden. Instead of deleting, discard "
                                 "the operation that created this element.")

        self.__operations_results.append(None)

    def __add_entity_property(self, request):
        entity_xml_id = request['edited_element_id']
        entity_xml_id = self.__update_target_xml_id(entity_xml_id)

        if entity_xml_id != request['edited_element_id']:
            request['edited_element_id'] = entity_xml_id

        entity_property = request['parameters']
        entity_type = self.__db_handler.get_entity_type(entity_xml_id)

        if entity_type in self.__listable_entities_types:
            property_id = self.__db_handler.add_entity_property(entity_xml_id, entity_property)

        else:
            property_id = self.__db_handler.add_entity_property(entity_xml_id, entity_property)

            body_content = self.__db_handler.get_body_content()
            body_content = self.__xml_handler.add_entity_properties(body_content, entity_xml_id, entity_property)
            self.__db_handler.set_body_content(body_content)

        self.__operations_results.append(property_id)

    def __modify_entity_property(self, request):
        entity_xml_id = request['edited_element_id']
        property_name = request['old_element_id']
        new_entity_property = request['parameters']
        entity_type = self.__db_handler.get_entity_type(entity_xml_id)

        if entity_type in self.__listable_entities_types:
            property_id, saved = self.__db_handler.modify_entity_property(entity_xml_id, new_entity_property,
                                                                          property_name)

        else:
            old_property_value = self.__db_handler.get_entity_property_value(entity_xml_id, property_name)
            old_entity_property = {property_name: old_property_value}

            property_id, saved = self.__db_handler.modify_entity_property(entity_xml_id, new_entity_property,
                                                                          property_name)

            body_content = self.__db_handler.get_body_content()
            body_content = self.__xml_handler.modify_entity_property(body_content, entity_xml_id, old_entity_property,
                                                                     new_entity_property)
            self.__db_handler.set_body_content(body_content)

        self.__operations_results.append(property_id)

        return saved

    def __delete_entity_property(self, request):
        entity_xml_id = request['edited_element_id']
        property_name = request['old_element_id']
        entity_type = self.__db_handler.get_entity_type(entity_xml_id)

        if entity_type in self.__listable_entities_types:
            try:
                self.__db_handler.delete_entity_property(entity_xml_id, property_name)
            except UnsavedElement:
                raise BadRequest("Deleting an unsaved element is forbidden. Instead of deleting, discard "
                                 "the operation that created this element.")

        else:
            property_value = self.__db_handler.get_entity_property_value(entity_xml_id, property_name)
            entity_property = {property_name: property_value}

            try:
                self.__db_handler.delete_entity_property(entity_xml_id, property_name)
            except UnsavedElement:
                raise BadRequest("Deleting an unsaved element is forbidden. Instead of deleting, discard "
                                 "the operation that created this element.")

            body_content = self.__db_handler.get_body_content()
            body_content = self.__xml_handler.delete_entity_properties(body_content, entity_xml_id, entity_property)
            self.__db_handler.set_body_content(body_content)

        self.__operations_results.append(None)

    def __add_certainty(self, request):
        certainty_target = request['new_element_id']
        certainty_target = self.__update_target_xml_id(certainty_target)
        parameters = request['parameters']

        if certainty_target != request['new_element_id']:
            request['new_element_id'] = certainty_target

        certainty_xml_id = self.__db_handler.add_certainty(certainty_target, parameters)

        self.__operations_results.append(certainty_xml_id)

    def __modify_certainty(self, request):
        certainty_xml_id = request['edited_element_id']
        parameter_name = request['old_element_id']
        new_value = request['parameters']

        saved = self.__db_handler.modify_certainty(certainty_xml_id, parameter_name, new_value)

        self.__operations_results.append(certainty_xml_id)

        return saved

    def __delete_certainty(self, request):
        certainty_xml_id = request['edited_element_id']

        try:
            self.__db_handler.delete_certainty(certainty_xml_id)
        except UnsavedElement:
            raise BadRequest("Deleting an unsaved element is forbidden. Instead of deleting, discard "
                             "the operation that created this element.")

        self.__operations_results.append(None)

    def __discard_adding_tag(self, operation):
        tag_xml_id = operation['operation_result']

        body_content = self.__db_handler.get_body_content()
        body_content = self.__xml_handler.discard_adding_tag(body_content, tag_xml_id)
        self.__db_handler.set_body_content(body_content)

    def __discard_moving_tag(self, operation):
        tag_xml_id = operation['operation_result']

        body_content = self.__db_handler.get_body_content()
        body_content = self.__xml_handler.discard_moving_tag(body_content, tag_xml_id)
        self.__db_handler.set_body_content(body_content)

    def __discard_deleting_tag(self, operation):
        tag_xml_id = operation['edited_element_id']

        body_content = self.__db_handler.get_body_content()
        body_content = self.__xml_handler.discard_deleting_tag(body_content, tag_xml_id)
        self.__db_handler.set_body_content(body_content)

    def __discard_adding_reference(self, operation):
        tag_xml_id = operation['edited_element_id']
        entity_xml_id = operation['operation_result']

        entity_type = self.__db_handler.get_entity_type(entity_xml_id)
        properties_added = None

        if entity_type not in self.__listable_entities_types:
            entity_properties_values = self.__db_handler.get_entity_properties_values(entity_xml_id,
                                                                                      include_unsaved=True)
            properties_added = list(entity_properties_values.keys())

        body_content = self.__db_handler.get_body_content()
        body_content = self.__xml_handler.discard_adding_reference_to_entity(body_content, tag_xml_id,
                                                                             properties_added)
        self.__db_handler.set_body_content(body_content)

        last_reference = self.__xml_handler.check_if_last_reference(body_content, entity_xml_id)
        self.__db_handler.discard_adding_reference_to_entity(entity_xml_id, last_reference)

    def __discard_modifying_reference(self, operation):
        tag_xml_id = operation['edited_element_id']
        new_entity_xml_id = operation['operation_result']
        old_entity_xml_id = operation['old_element_id']

        old_entity_type = self.__db_handler.get_entity_type(old_entity_xml_id)
        new_entity_type = self.__db_handler.get_entity_type(new_entity_xml_id)
        properties_added = None
        properties_deleted = None

        if old_entity_type not in self.__listable_entities_types:
            old_entity_properties_values = self.__db_handler.get_entity_properties_values(old_entity_xml_id,
                                                                                          include_unsaved=True)
            properties_deleted = list(old_entity_properties_values.keys())

        if new_entity_type not in self.__listable_entities_types:
            new_entity_properties_values = self.__db_handler.get_entity_properties_values(new_entity_xml_id,
                                                                                          include_unsaved=True)
            properties_added = list(new_entity_properties_values.keys())

        body_content = self.__db_handler.get_body_content()
        body_content = self.__xml_handler.discard_modifying_reference_to_entity(body_content, tag_xml_id,
                                                                                properties_added, properties_deleted)
        self.__db_handler.set_body_content(body_content)

        last_reference = self.__xml_handler.check_if_last_reference(body_content, new_entity_xml_id)
        self.__db_handler.discard_modifying_reference_to_entity(old_entity_xml_id, new_entity_xml_id, last_reference)

    def __discard_removing_reference(self, operation):
        tag_xml_id = operation['edited_element_id']
        old_entity_xml_id = operation['old_element_id']

        old_entity_type = self.__db_handler.get_entity_type(old_entity_xml_id)
        properties_deleted = None

        if old_entity_type not in self.__listable_entities_types:
            old_entity_properties_values = self.__db_handler.get_entity_properties_values(old_entity_xml_id,
                                                                                          include_unsaved=True)
            properties_deleted = list(old_entity_properties_values.keys())

        body_content = self.__db_handler.get_body_content()
        body_content = self.__xml_handler.discard_removing_reference_to_entity(body_content, tag_xml_id,
                                                                               properties_deleted)
        self.__db_handler.set_body_content(body_content)

        self.__db_handler.discard_removing_reference_to_entity(old_entity_xml_id)

    def __discard_adding_entity_property(self, operation):
        entity_xml_id = operation['edited_element_id']
        property_name = operation['operation_result'].split('/')[1]

        entity_type = self.__db_handler.get_entity_type(entity_xml_id)

        if entity_type in self.__listable_entities_types:
            self.__db_handler.discard_adding_entity_property(entity_xml_id, property_name)

        else:
            body_content = self.__db_handler.get_body_content()
            body_content = self.__xml_handler.discard_adding_entity_property(body_content, entity_xml_id, property_name)

            self.__db_handler.set_body_content(body_content)

            self.__db_handler.discard_adding_entity_property(entity_xml_id, property_name)

    def __discard_modifying_entity_property(self, operation):
        entity_xml_id = operation['edited_element_id']
        property_name = operation['old_element_id']

        entity_type = self.__db_handler.get_entity_type(entity_xml_id)

        if entity_type in self.__listable_entities_types:
            self.__db_handler.discard_modifying_entity_property(entity_xml_id, property_name)

        else:
            body_content = self.__db_handler.get_body_content()
            body_content = self.__xml_handler.discard_modifying_entity_property(body_content, entity_xml_id,
                                                                                property_name)
            self.__db_handler.set_body_content(body_content)

            self.__db_handler.discard_modifying_entity_property(entity_xml_id, property_name)

    def __discard_removing_entity_property(self, operation):
        entity_xml_id = operation['edited_element_id']
        property_name = operation['old_element_id']

        entity_type = self.__db_handler.get_entity_type(entity_xml_id)

        if entity_type in self.__listable_entities_types:
            self.__db_handler.discard_removing_entity_property(entity_xml_id, property_name)

        else:
            body_content = self.__db_handler.get_body_content()
            body_content = self.__xml_handler.discard_removing_entity_property(body_content, entity_xml_id,
                                                                               property_name)
            self.__db_handler.set_body_content(body_content)

            self.__db_handler.discard_removing_entity_property(entity_xml_id, property_name)

    def __discard_adding_certainty(self, operation):
        certainty_xml_id = operation['operation_result']

        self.__db_handler.discard_adding_certainty(certainty_xml_id)

    def __discard_modifying_certainty(self, operation):
        certainty_xml_id = operation['operation_result']

        self.__db_handler.discard_modifying_certainty(certainty_xml_id)

    def __discard_removing_certainty(self, operation):
        certainty_xml_id = operation['edited_element_id']

        self.__db_handler.discard_removing_certainty(certainty_xml_id)

    def __accept_adding_tag(self, operation):
        tag_xml_id = operation['operation_result']

        body_content = self.__db_handler.get_body_content()
        body_content = self.__xml_handler.accept_adding_tag(body_content, tag_xml_id)
        self.__db_handler.set_body_content(body_content)

    def __accept_moving_tag(self, operation):
        tag_xml_id = operation['operation_result']

        body_content = self.__db_handler.get_body_content()
        body_content = self.__xml_handler.accept_moving_tag(body_content, tag_xml_id)
        self.__db_handler.set_body_content(body_content)

    def __accept_deleting_tag(self, operation):
        tag_xml_id = operation['edited_element_id']

        body_content = self.__db_handler.get_body_content()
        body_content = self.__xml_handler.accept_deleting_tag(body_content, tag_xml_id)
        self.__db_handler.set_body_content(body_content)

    def __accept_adding_reference(self, operation, new_file_version):
        tag_xml_id = operation['edited_element_id']
        entity_xml_id = operation['operation_result']

        entity_type = self.__db_handler.get_entity_type(entity_xml_id)
        properties_added = None

        if entity_type not in self.__listable_entities_types:
            entity_properties_values = self.__db_handler.get_entity_properties_values(entity_xml_id,
                                                                                      include_unsaved=True)
            properties_added = list(entity_properties_values.keys())

        body_content = self.__db_handler.get_body_content()
        body_content = self.__xml_handler.accept_adding_reference_to_entity(body_content, tag_xml_id, properties_added)
        self.__db_handler.set_body_content(body_content)

        self.__db_handler.accept_adding_reference_to_entity(entity_xml_id, new_file_version)

    def __accept_modifying_reference(self, operation, new_file_version):
        tag_xml_id = operation['edited_element_id']
        new_entity_xml_id = operation['operation_result']
        old_entity_xml_id = operation['old_element_id']

        old_entity_type = self.__db_handler.get_entity_type(old_entity_xml_id)
        new_entity_type = self.__db_handler.get_entity_type(new_entity_xml_id)
        properties_added = None
        properties_deleted = None

        if old_entity_type not in self.__listable_entities_types:
            properties_deleted = self.__db_handler.get_entity_properties_values(old_entity_xml_id,
                                                                                include_unsaved=True)

        if new_entity_type not in self.__listable_entities_types:
            properties_added = self.__db_handler.get_entity_properties_values(new_entity_xml_id, include_unsaved=True)

        body_content = self.__db_handler.get_body_content()
        body_content = self.__xml_handler.accept_modifying_reference_to_entity(body_content, tag_xml_id,
                                                                                properties_added, properties_deleted)
        self.__db_handler.set_body_content(body_content)

        last_reference = self.__xml_handler.check_if_last_reference(body_content, old_entity_xml_id)

        self.__db_handler.accept_modifying_reference_to_entity(old_entity_xml_id, new_entity_xml_id, new_file_version,
                                                               last_reference)

    def __accept_removing_reference(self, operation, new_file_version):
        tag_xml_id = operation['edited_element_id']
        entity_xml_id = operation['old_element_id']

        entity_type = self.__db_handler.get_entity_type(entity_xml_id)
        properties_deleted = None

        if entity_type not in self.__listable_entities_types:
            properties_deleted = self.__db_handler.get_entity_properties_values(entity_xml_id, include_unsaved=True)

        body_content = self.__db_handler.get_body_content()
        body_content = self.__xml_handler.accept_removing_reference_to_entity(body_content, tag_xml_id,
                                                                              properties_deleted)
        self.__db_handler.set_body_content(body_content)

        last_reference = self.__xml_handler.check_if_last_reference(body_content, entity_xml_id)

        self.__db_handler.accept_removing_reference_to_entity(entity_xml_id, new_file_version, last_reference)

    def __accept_adding_entity_property(self, operation, new_file_version):
        entity_xml_id = operation['edited_element_id']
        property_name = operation['operation_result'].split('/')[1]

        entity_type = self.__db_handler.get_entity_type(entity_xml_id)

        if entity_type in self.__listable_entities_types:
            self.__db_handler.accept_adding_entity_property(entity_xml_id, property_name, new_file_version)

        else:
            body_content = self.__db_handler.get_body_content()
            body_content = self.__xml_handler.accept_adding_entity_property(body_content, entity_xml_id, property_name)

            self.__db_handler.set_body_content(body_content)

            self.__db_handler.accept_adding_entity_property(entity_xml_id, property_name, new_file_version)

    def __accept_modifying_entity_property(self, operation, new_file_version):
        entity_xml_id = operation['edited_element_id']
        property_name = operation['old_element_id']

        entity_type = self.__db_handler.get_entity_type(entity_xml_id)

        if entity_type in self.__listable_entities_types:
            self.__db_handler.accept_modifying_entity_property(entity_xml_id, property_name, new_file_version)

        else:
            body_content = self.__db_handler.get_body_content()
            body_content = self.__xml_handler.accept_modifying_entity_property(body_content, entity_xml_id,
                                                                               property_name)
            self.__db_handler.set_body_content(body_content)

            self.__db_handler.accept_modifying_entity_property(entity_xml_id, property_name, new_file_version)

    def __accept_removing_entity_property(self, operation, new_file_version):
        entity_xml_id = operation['edited_element_id']
        property_name = operation['old_element_id']

        entity_type = self.__db_handler.get_entity_type(entity_xml_id)

        if entity_type in self.__listable_entities_types:
            self.__db_handler.accept_removing_entity_property(entity_xml_id, property_name, new_file_version)

        else:
            body_content = self.__db_handler.get_body_content()
            body_content = self.__xml_handler.accept_removing_entity_property(body_content, entity_xml_id,
                                                                              property_name)
            self.__db_handler.set_body_content(body_content)

            self.__db_handler.accept_removing_entity_property(entity_xml_id, property_name, new_file_version)

    def __accept_adding_certainty(self, operation, new_file_version):
        certainty_xml_id = operation['operation_result']

        self.__db_handler.accept_adding_certainty(certainty_xml_id, new_file_version)

    def __accept_modifying_certainty(self, operation, new_file_version):
        certainty_xml_id = operation['operation_result']

        self.__db_handler.accept_modifying_certainty(certainty_xml_id, new_file_version)

    def __accept_removing_certainty(self, operation, new_file_version):
        certainty_xml_id = operation['edited_element_id']

        self.__db_handler.accept_removing_certainty(certainty_xml_id, new_file_version)

    def __clean_operation_results(self):
        self.__operations_results = []

    def __start_saving_file(self):
        new_file_version = self.__db_handler.get_new_file_version()

        return new_file_version

    def __finish_saving_file(self, new_file_version):
        old_xml_content = self.__db_handler.get_previous_xml_content()
        new_body_content = self.__db_handler.get_body_content()

        new_xml_content = self.__xml_handler.switch_body_content(old_xml_content, new_body_content)

        self.__db_handler.finish_creating_new_file_version(new_file_version, new_xml_content)

    def __update_target_xml_id(self, target):
        if target is None:
            new_target = target

        elif isinstance(target, int):
            new_target = self.__operations_results[target]

        elif '@' in target:
            new_target = self.__update_target_xml_id_with_argument(target, '@')

        elif '/' in target:
            new_target = self.__update_target_xml_id_with_argument(target, '/')

        else:
            new_target = target

        return new_target

    def __update_target_xml_id_with_argument(self, target, separator):
        splitted = target.split(separator)

        xml_id_part = splitted[0]
        argument_part = splitted[1]

        try:
            operation_id = int(xml_id_part)
            xml_id = self.__operations_results[operation_id]

            new_target = f'{xml_id}{separator}{argument_part}'

        except ValueError:
            new_target = target

        return new_target

    def __get_new_tag_xml_id(self, tag_xml_id, new_tag):
        edited_element_id_base = tag_xml_id.split('-')[0]

        if edited_element_id_base != new_tag:
            new_tag_xml_id = self.__db_handler.get_next_xml_id(new_tag)

        else:
            new_tag_xml_id = None

        return new_tag_xml_id

    def __find_dependencies(self, operation, operation_result, modification=False):
        dependencies_ids = []

        if operation['element_type'] == 'reference':
            tag_xml_id = operation['edited_element_id']
            entity_xml_id = operation_result
            body_content = self.__db_handler.get_body_content()

            try:
                self.__xml_handler.check_if_tag_is_saved(body_content, tag_xml_id)

            except UnsavedElement:
                operation_id = self.__db_handler.get_operation_id_that_created_tag(tag_xml_id)
                dependencies_ids.append(operation_id)

            if 'new_element_id' in operation and operation['new_element_id'] is not None:
                try:
                    self.__db_handler.check_if_entity_is_saved(entity_xml_id)

                except UnsavedElement:
                    operation_id = self.__db_handler.get_operation_id_that_created_entity(entity_xml_id)
                    dependencies_ids.append(operation_id)

        elif operation['element_type'] == 'entity_property':
            entity_xml_id = operation['edited_element_id']

            try:
                self.__db_handler.check_if_entity_is_saved(entity_xml_id)

            except UnsavedElement:
                operation_id = self.__db_handler.get_operation_id_that_created_entity(entity_xml_id)
                dependencies_ids.append(operation_id)

        elif operation['element_type'] == 'certainty':
            if not modification:
                certainty_target = operation['new_element_id']
                locus = operation['parameters']['locus']

            else:
                certainty_target = operation['edited_element_id']
                locus = self.__db_handler.get_certainty_locus(certainty_target)

            certainty_target = self.__update_target_xml_id(certainty_target)

            target_type = self.__db_handler.get_certainty_target_type(certainty_target, locus)
            target, match = self.__db_handler.get_certainty_target_and_match(certainty_target, target_type)

            if target_type == ElementTypes.text:
                body_content = self.__db_handler.get_body_content()

                try:
                    self.__xml_handler.check_if_tag_is_saved(body_content, target)

                except UnsavedElement:
                    operation_id = self.__db_handler.get_operation_id_that_created_tag(target)
                    dependencies_ids.append(operation_id)

            elif target_type == ElementTypes.reference:
                body_content = self.__db_handler.get_body_content()

                try:
                    self.__xml_handler.check_if_reference_is_saved(body_content, target)

                except UnsavedElement:
                    operation_id = self.__db_handler.get_operation_id_that_created_reference(target)
                    dependencies_ids.append(operation_id)

            elif target_type == ElementTypes.entity_type:
                try:
                    self.__db_handler.check_if_entity_is_saved(target)

                except UnsavedElement:
                    operation_id = self.__db_handler.get_operation_id_that_created_entity(target)
                    dependencies_ids.append(operation_id)

            elif target_type == ElementTypes.entity_property:
                property_name = certainty_target.split('/')[-1]

                try:
                    self.__db_handler.check_if_entity_property_is_saved(target, property_name)

                except UnsavedElement:
                    operation_id = self.__db_handler.get_operation_id_that_created_entity_property(target,
                                                                                                   property_name)
                    dependencies_ids.append(operation_id)

            elif target_type == ElementTypes.certainty:
                try:
                    self.__db_handler.check_if_certainty_is_saved(target)

                except UnsavedElement:
                    operation_id = self.__db_handler.get_operation_id_that_created_certainty(target)
                    dependencies_ids.append(operation_id)

        return dependencies_ids

    def __verify_if_dependencies_will_be_saved(self, operations):
        operations_ids = [operation['id'] for operation in operations]

        for operation_id in operations_ids:
            dependencies_ids = self.__db_handler.get_operation_dependencies_ids(operation_id)

            if dependencies_ids and not any(id in dependencies_ids for id in operations_ids):
                dependencies_ids = [str(dependency_id) for dependency_id in dependencies_ids]
                dependencies_ids = ', '.join(dependencies_ids)

                raise BadRequest(f"Operation with id: {operation_id} cannot be saved, because dependent operations "
                                 f"with ids: {dependencies_ids} have not been saved")
