from typing import List

from apps.api_vis.enums import TypeChoice
from apps.api_vis.models import Entity, EntityVersion, EntityProperty
from apps.nn_disambiguator import names, time, geography
from apps.projects.models import EntitySchema
from collaborative_platform.settings import DEFAULT_ENTITIES


class DataProcessor:
    processing_functions: {
        TypeChoice.str: {
            names.nlp_sim,
            names.levenshtein_distance,
            names.phonetics_sim,
            names.ratcliff_obershelp_sim
        },
        TypeChoice.date: {
            time.days_apart
        },
        TypeChoice.time: {
            time.days_apart
        },
        TypeChoice.Point: {
            geography.distance
        }
    }

    def __init__(self, entity_type: EntitySchema):
        entity_settings = DEFAULT_ENTITIES.get(entity_type.name, None)
        self.properties = entity_settings['properties'] or {'name': {'type': TypeChoice.str}}

    def __calculate_similarity(self, e1: EntityVersion, e2: EntityVersion) -> List[float]:
        sims = []
        for property, params in self.properties.items():
            try:
                p1 = e1.properties.get(name=property)
            except EntityProperty.DoesNotExist:
                p1 = None

            try:
                p2 = e2.properties.get(name=property)
            except EntityProperty.DoesNotExist:
                p2 = None

            for f in self.processing_functions[params['type']]:
                if p1 is None or p2 is None:
                    sims.append(-1)
                else:
                    sims.append(f(p1.get_value(), p2.get_value()))

        return sims
