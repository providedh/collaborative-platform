import itertools
from typing import List

from sklearn.exceptions import NotFittedError
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

from apps.api_vis.enums import TypeChoice
from apps.api_vis.models import EntityVersion, EntityProperty, Entity
from apps.nn_disambiguator import names, time, geography
from apps.nn_disambiguator.models import Classifier
from apps.projects.models import EntitySchema, Project
from collaborative_platform.settings import DEFAULT_ENTITIES
import spacy


class SimilarityCalculator:
    nlp = spacy.load('en_core_web_lg')

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
            time.seconds_apart
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
                    sims.append(0)
                else:
                    sims.append(f(p1.get_value(), p2.get_value()))

        return sims

    def __calculate_files_text_similarity(self, e1lv, e2lv) -> float:
        if e1lv.file_version == e2lv.file_version:
            return 1.0
        else:
            nlp_file1 = self.nlp(e1lv.file_version.body_text)
            nlp_file2 = self.nlp(e2lv.file_version.body_text)
            return nlp_file1.similarity(nlp_file2)

    def __calculate_features_vector_length(self, schema: EntitySchema) -> int:
        v = 1  # 1 for files text similarity
        entity = DEFAULT_ENTITIES.get(schema.name)
        if entity is not None:
            for property, values in entity["properties"]:
                v += len(self.processing_functions[values["type"]])
        else:
            v += len(self.processing_functions[TypeChoice.str])  # only name

        # 1 number for avg similarity between files of each of the other types of entities
        v += schema.taxonomy.entities_schemas.count() - 1
        return v

    def __calculate_other_entities_avg_similarity(self, e1v: EntityVersion, e2v: EntityVersion, files_sim: float) -> \
            List[float]:
        schemas = e1v.file_version.file.project.taxonomy.entities_schemas.all()
        sims = []

        for schema in schemas:
            try:
                clf = Classifier.objects.get(entity_schema=schema)
            except Classifier.DoesNotExist:
                continue

            model: MLPClassifier = clf.get_model()
            scaler: StandardScaler = clf.get_scaler()

            try:
                model.predict([0 for _ in range(self.__calculate_features_vector_length(schema))])
            except NotFittedError:
                sims.append(0)
                continue

            file_1_entities = e1v.file_version.entityversion_set.filter(entity__type=schema.name)
            file_2_entities = e2v.file_version.entityversion_set.filter(entity__type=schema.name)

            pairs = set(itertools.product(file_1_entities, file_2_entities))
            pairs.remove((e1v, e2v))

            avg = 0
            for _e1v, _e2v in pairs:
                fv = self.__calculate_similarity(_e1v, _e2v)
                fv.append(files_sim)
                fv.extend([0 for _ in range(_e1v.file_version.file.project.taxonomy.entities_schemas.count())])
                fv = scaler.transform([fv])
                avg += model.predict_proba(fv)[0][1]
            avg /= len(pairs)
            sims.append(avg)

        return sims

    def get_features_vector(self, e1: Entity, e2: Entity) -> List[float]:
        e1lv = e1.versions.latest('id')
        e2lv = e2.versions.latest('id')

        sims = self.__calculate_similarity(e1lv, e2lv)

        files_sim = self.__calculate_files_text_similarity(e1lv, e2lv)
        sims.append(files_sim)

        other_entities_sims = self.__calculate_other_entities_avg_similarity(e1lv, e2lv, files_sim)
        sims.extend(other_entities_sims)

        return sims
