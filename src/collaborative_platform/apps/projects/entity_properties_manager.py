class Attribute:
    def __init__(self, name: str, parent):
        self.parent = parent
        self.name: str = name

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    def get_xpath(self):
        return f"{self.parent.get_xpath()}@{self.name}"


class Element(Attribute):
    def __init__(self, name: str, parent=None):
        super().__init__(name, parent)
        self.attributes: set = set()
        self.sub_elements: set = set()

    def add_attribute(self, name: str):
        self.attributes.add(Attribute(name=name, parent=self))

    def get_properties(self):
        properties = list(self.attributes)

        for elem in self.sub_elements:
            if len(elem.sub_elements) == 0:
                properties.append(elem)
            else:
                properties.extend(elem.get_properties())

        return properties

    def add_sub_element(self, element):
        element.parent = self
        self.sub_elements.add(element)

    def get_xpath(self):
        if self.parent is not None:
            return f"{self.parent.get_xpath()}/{self.name}"
        else:
            return self.name


class EntityPropertiesManager:
    entities_schema = {
        "person": {
            "attributes": ("sex", "age"),
            "sub-elements": {
                "persName": {"sub-elements": {"forename": {}, "surname": {}}},
                "occupation": {},
                "birth": {"attributes": ("when",)},
                "death": {"attributes": ("when",)}
            }
        },
        "event": {},
        "org": {},
        "place": {
            "sub-elements": {
                "country": {},
                "settlement": {},
                "location": {"sub-elements": {"geo": {}}}
            }
        },
        "date": {},
        "time": {},
    }

    def __init__(self, entities_schema=None):
        if entities_schema is None:
            entities_schema = self.entities_schema
        self.entities = [self.deserialize(name, contains) for name, contains in entities_schema.items()]

    @classmethod
    def deserialize(cls, name: str, entity: dict) -> Element:
        element = Element(name)

        for attr in entity.get("attributes", ()):
            element.add_attribute(attr)

        for name, contains in entity.get("sub-elements", dict()).items():
            element.add_sub_element(cls.deserialize(name, contains))

        return element


if __name__ == "__main__":
    e = EntityPropertiesManager()
    print([a for a in e.entities[0].get_properties()])
    pass
