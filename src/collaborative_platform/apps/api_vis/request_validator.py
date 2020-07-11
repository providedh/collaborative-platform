from apps.exceptions import BadRequest


class RequestValidator:
    @staticmethod
    def validate_clique_creation_data(request_data):
        required_keys = {
            'entities': list,
            'certainty': str,
            'project_version': float,
        }
        optional_keys = {
            'name': str
        }

        validate_keys_and_types(request_data, required_keys, optional_keys)

    @staticmethod
    def validate_clique_delete_data(request_data):
        required_keys = {
            'cliques': list,
            'project_version': float,
        }

        validate_keys_and_types(request_data, required_keys)

    @staticmethod
    def validate_put_clique_entities_data(request_data):
        required_keys = {
            'entities': list,
            'certainty': str,
            'project_version': float,
        }
        optional_keys = {
            'name': str
        }

        validate_keys_and_types(request_data, required_keys, optional_keys)

    @staticmethod
    def validate_delete_clique_entities_data(request_data):
        required_keys = {
            'entities': list,
            'project_version': float,
        }

        validate_keys_and_types(request_data, required_keys)

    @staticmethod
    def validate_commit_data(request_data):
        optional_keys = {
            'message': str,
        }

        validate_keys_and_types(request_data, optional_key_type_pairs=optional_keys)


def validate_keys_and_types(dictionary, required_key_type_pairs=None, optional_key_type_pairs=None, parent_name=None):
    # type: (dict, dict, dict, str) -> None

    if required_key_type_pairs:
        for key in required_key_type_pairs:
            if key not in dictionary:
                if not parent_name:
                    raise BadRequest(f"Missing '{key}' parameter in request data.")
                else:
                    raise BadRequest(f"Missing '{key}' parameter in {parent_name} argument in request data.")

            if type(dictionary[key]) is not required_key_type_pairs[key]:
                raise BadRequest(f"Invalid type of '{key}' parameter. "
                                 f"Correct type is: '{str(required_key_type_pairs[key])}'.")

    if optional_key_type_pairs:
        for key in optional_key_type_pairs:
            if key in dictionary and type(dictionary[key]) is not optional_key_type_pairs[key]:
                raise BadRequest(f"Invalid type of '{key}' parameter. "
                                 f"Correct type is: '{str(optional_key_type_pairs[key])}'.")
