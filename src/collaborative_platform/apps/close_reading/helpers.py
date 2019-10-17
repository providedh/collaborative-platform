from apps.files_management.models import File


def verify_reference(file_id, asserted_value):
    file = File.objects.get(id=file_id)
    path_to_file = file.get_relative_path()

    path_to_reference, person_id = asserted_value.split('#')

    if path_to_file == path_to_reference:
        asserted_value = '#' + person_id

    return asserted_value
