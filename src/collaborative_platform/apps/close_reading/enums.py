from enum import Enum


class ElementTypes(Enum):
    text = 1
    reference = 2
    entity_type = 3
    entity_property = 4
    certainty = 5


class Methods(Enum):
    POST = 1
    PUT = 2
    DELETE = 3
