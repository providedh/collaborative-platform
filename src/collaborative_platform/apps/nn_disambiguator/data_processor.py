from apps.api_vis.enums import TypeChoice
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
        properties = DEFAULT_ENTITIES[entity_type.name]["properties"]
