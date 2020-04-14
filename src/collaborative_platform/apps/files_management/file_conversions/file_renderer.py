from apps.files_management.helpers import append_unifications


class FileRenderer:
    def render_file_version(self, file_version):
        file_version.upload.open('r')
        xml_content = file_version.upload.read()
        file_version.upload.close()

        xml_content = append_unifications(xml_content, file_version)

        return xml_content
