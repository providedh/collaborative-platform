from django.forms.models import model_to_dict


class Serializer:
    @staticmethod
    def serialize_clique(clique):
        serialized_clique = model_to_dict(clique, ['id', 'name', 'type'])

        return serialized_clique

    @staticmethod
    def get_entities_ids(unifications):
        entities_ids = unifications.values_list('entity_id', flat=True)
        entities_ids = list(entities_ids)

        return entities_ids

    @staticmethod
    def serialize_entity(entity):
        serialized_entity = model_to_dict(entity, ['id', 'type'])

        return serialized_entity
