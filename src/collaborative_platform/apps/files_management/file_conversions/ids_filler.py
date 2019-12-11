import re
import io
from lxml import etree as et

from apps.files_management.file_conversions.xml_formatter import XMLFormatter
from apps.files_management.file_conversions.tei_handler import TeiHandler
from apps.files_management.models import FileMaxXmlIds
from apps.index_and_search.entities_extractor import EntitiesExtractor


class IDsFiller:
    _tags = ('person', 'place', 'org', 'event', 'certainty')
    _namespaces = {'tei': 'http://www.tei-c.org/ns/1.0', 'xml': 'http://www.w3.org/XML/1998/namespace'}

    def __init__(self, contents, filename, file_id=None):
        self._maxid = None
        if type(contents) is TeiHandler:
            self.__contents = contents.get_text()
            self.__message = contents.get_message()
        elif type(contents) is str:
            self.__contents = contents
            self.__message = ""

        self.text = io.StringIO()
        self._parsed = et.fromstring(bytes(self.__contents, 'utf-8'))
        filename = filename[:-4] if filename[-4:] == ".xml" else filename
        self.filename = filename.replace(' ', '_').replace('(', '').replace(')', '')
        self._file_id = file_id

    def __fill_tags(self):
        grouped_tags = EntitiesExtractor.extract_entities_elements(self._parsed)

        modified = False

        for tag, elements in grouped_tags.items():
            for element in elements:
                if element.attrib.get("{{{}}}id".format(self._namespaces['xml'])) is None:
                    modified = True
                    self._maxid[tag] += 1
                    element.attrib['{{{}}}id'.format(self._namespaces['xml'])] = "{}_{}-{}".format(tag, self.filename,
                                                                                                   self._maxid[tag])
        return modified

    def __find_max_ids(self):
        self._maxid = dict()
        for tag in self._tags:
            ids = re.findall('xml:id="{}_{}-[0-9]+?"'.format(tag, self.filename), self.__contents)
            ids = [id.split('-')[-1][:-1] for id in ids]
            self._maxid[tag] = max(map(int, ids)) if ids else 0

    def __get_max_ids(self):
        if self._file_id is None:
            raise ResourceWarning("No file_id given on initialization, cannot retrieve max_ids from database.")
        dbo = FileMaxXmlIds.objects.get(file_id=self._file_id)  # type: FileMaxXmlIds
        self._maxid = dict(zip(self._tags, (dbo.person, dbo.place, dbo.org, dbo.event, dbo.certainty)))

    def __update_max_ids(self):
        if self._file_id is None:
            raise ResourceWarning("No file_id given on initialization, cannot retrieve max_ids from database.")
        dbo = FileMaxXmlIds.objects.get(file_id=self._file_id)
        dbo.event = self._maxid["event"]
        dbo.person = self._maxid["person"]
        dbo.place = self._maxid["place"]
        dbo.org = self._maxid["org"]
        dbo.certainty = self._maxid["certainty"]
        dbo.save()

    def __replace_all(self):
        grouped_tags = EntitiesExtractor.extract_entities_elements(self._parsed)

        original_ids_map = {}

        for tag, elements in grouped_tags.items():
            for element in elements:
                org = element.attrib.get("{{{}}}id".format(self._namespaces['xml']))
                self._maxid[tag] += 1
                new = "{}_{}-{}".format(tag, self.filename, self._maxid[tag])
                element.attrib['{{{}}}id'.format(self._namespaces['xml'])] = new
                original_ids_map[org] = new

        try:
            original_ids_map.pop(None)
        except KeyError:
            pass
        return original_ids_map

    def __alter_not_indexed_ids(self, text):
        ids_map = {}

        def process_match(match):
            tag_name = match.group(1)
            if tag_name in self._tags:
                return match.group(0)
            result = "<" + tag_name + match.group(2) + 'xml:id="'
            id_no = self._maxid.get(tag_name, 0)
            new_id = f"{tag_name}_{self.filename}-{id_no}"
            result += new_id
            result += '"' + match.group(4)
            ids_map[match.group(3)] = new_id
            self._maxid[tag_name] = id_no + 1
            return result

        text = re.sub(r"<([a-zA-Z_][a-zA-Z\-_.]*)([^>]*?)xml:id=['\"]([^>\"']*?)['\"]([^>]*?>)",
                      process_match, text)

        for old, new in ids_map.items():
            text = text.replace("='" + old, "='" + new).replace('="' + old, '="' + new)
        return text

    def process(self, initial=False):
        if initial:
            self.__get_max_ids()
            ids_map = self.__replace_all()
            text = et.tostring(self._parsed, pretty_print=True, encoding='utf-8').decode('utf-8')

            for old, new in ids_map.items():
                text = text.replace("='" + old, "='" + new).replace('="' + old, '="' + new)

            text = self.__alter_not_indexed_ids(text)

            xml_formatter = XMLFormatter()
            text = xml_formatter.reformat_xml(text)

            self.text = io.StringIO(text)
            self.text.seek(io.SEEK_SET)
            self.__update_max_ids()
        else:
            self.__get_max_ids()
            if self.__fill_tags():
                text = et.tostring(self._parsed, pretty_print=True, encoding='utf-8').decode('utf-8')

                xml_formatter = XMLFormatter()
                text = xml_formatter.reformat_xml(text)

                self.text = io.StringIO(text)
                self.text.seek(io.SEEK_SET)

                if self.__message:
                    self.__message += " "

                self.__message += "Filled in missing ids of entities in file."
                self.__update_max_ids()
                return True
            else:
                self.text = io.StringIO(self.__contents)
                self.text.seek(io.SEEK_SET)
                return False  # no change needed

    def get_message(self):
        return self.__message

    def close(self):
        self.text.close()

    async def read(self, size=-1):
        chunk = self.text.read(size)

        return bytes(chunk, "utf-8")

    async def _read(self, size):
        pass

    def size(self):
        pass

    def get_text(self):
        return self.text.getvalue()
