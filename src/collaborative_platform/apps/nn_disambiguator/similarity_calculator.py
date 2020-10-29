import itertools
import sys
import numpy as np
from typing import List, Tuple

from lxml import etree
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

from apps.api_vis.enums import TypeChoice
from apps.api_vis.models import EntityVersion, EntityProperty, Entity
from apps.nn_disambiguator import names, time, geography
from apps.nn_disambiguator.models import Classifier, SimilarityCache, FileTextSimilarityCache
from apps.projects.models import EntitySchema, Taxonomy
from collaborative_platform import settings
from collaborative_platform.settings import DEFAULT_ENTITIES, CUSTOM_ENTITY
import spacy


class SimilarityCalculator:
    nlp = spacy.load('en_core_web_lg')
    namespaces = settings.XML_NAMESPACES

    processing_functions = {
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

    def __calculate_similarity(self, e1: EntityVersion, e2: EntityVersion) -> List[float]:
        sims = []

        entity_settings = DEFAULT_ENTITIES.get(e1.entity.type, None)
        properties = entity_settings['properties'] if entity_settings is not None else CUSTOM_ENTITY['properties']

        for property, params in properties.items():
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

    def __calculate_files_text_similarity(self, e1lv, e2lv) -> float:
        if e1lv.file_version == e2lv.file_version:
            return 1.
        elif e1lv.file_version is None or e2lv.file_version is None:
            return 0.
        else:
            ftsc, created = FileTextSimilarityCache.objects.get_or_create(fv1=e1lv.file_version, fv2=e2lv.file_version)
            if created:
                nlp_file1 = self.nlp(e1lv.file_version.body_text)
                nlp_file2 = self.nlp(e2lv.file_version.body_text)
                ftsc.sim = nlp_file1.similarity(nlp_file2)
                ftsc.save()
            return ftsc.sim

    def __calculate_other_entities_avg_similarity(self, e1v: EntityVersion, e2v: EntityVersion,
                                                  files_text_sim: float) -> List[float]:
        schemas = e1v.file_version.file.project.taxonomy.entities_schemas.all()
        sims = []

        unifiable_schemas = self.count_unifiable_schemas(e1v.file_version.file.project.taxonomy)

        for schema in schemas:
            schema_settings = DEFAULT_ENTITIES.get(schema.name, None)
            if schema_settings is not None and not schema_settings["unifiable"]:
                continue

            try:
                clf = Classifier.objects.get(entity_schema=schema)
            except Classifier.DoesNotExist:
                continue

            model: MLPClassifier = clf.get_model()
            scaler: StandardScaler = clf.get_scaler()

            file_1_entities = e1v.file_version.entityversion_set.filter(entity__type=schema.name)
            file_2_entities = e2v.file_version.entityversion_set.filter(entity__type=schema.name)

            pairs = set(itertools.product(file_1_entities, file_2_entities))

            try:
                pairs.remove((e1v, e2v))
            except KeyError:
                pass

            if len(pairs) == 0:
                sims.append(-1)
                continue

            avg = 0
            for _e1v, _e2v in pairs:
                try:
                    if SimilarityCache.objects.filter(e1v=_e1v, e2v=_e2v).exists():
                        sc = SimilarityCache.objects.get(e1v=_e1v, e2v=_e2v)
                    elif SimilarityCache.objects.filter(e1v=_e2v, e2v=_e1v).exists():
                        sc = SimilarityCache.objects.get(e1v=_e2v, e2v=_e1v)
                    else:
                        raise SimilarityCache.DoesNotExist
                except SimilarityCache.DoesNotExist:
                    fv = self.__calculate_similarity(_e1v, _e2v)
                    fv.append(files_text_sim)
                    fv.extend([0] * unifiable_schemas)
                    fv.extend(self.__calculate_files_creation_dates_and_places(_e1v, _e2v))
                else:
                    fv = sc.vector
                finally:
                    fv = scaler.transform([fv])
                    avg += model.predict_proba(fv)[0][1]

            avg /= len(pairs)
            sims.append(avg)

        return sims

    def __calculate_files_creation_dates_and_places(self, e1v: EntityVersion, e2v: EntityVersion) -> Tuple[int, float]:
        def get_date_and_place(ev):
            try:
                et = etree.fromstring(ev.file_version.get_raw_content())
            except ValueError:
                et = etree.fromstring(ev.file_version.get_raw_content().encode())

            creation = et.xpath(".//tei:creation", namespaces=self.namespaces)
            if creation:
                creation = creation[0]
            else:
                return sys.maxsize, sys.maxsize

            place = ' '.join(map(str.strip, creation.itertext())).strip()

            date = creation.xpath("tei:date", namespaces=self.namespaces)
            if date:
                date = date[0]
            else:
                return sys.maxsize, place

            return date.get("when"), place

        d1, p1 = get_date_and_place(e1v)
        d2, p2 = get_date_and_place(e2v)

        dt = time.days_apart(d1, d2)
        distance = geography.names_to_distance(p1, p2) if p1 and p2 else sys.maxsize

        return dt, distance

    def calculate_features_vector_length(self, schema: EntitySchema) -> int:
        v = 1  # 1 for files text similarity
        entity = DEFAULT_ENTITIES.get(schema.name) or CUSTOM_ENTITY

        for _, values in entity["properties"].items():
            v += len(self.processing_functions[values["type"]])

        # 1 number for avg similarity between files of each of the other types of entities
        v += self.count_unifiable_schemas(schema.taxonomy)

        # Files creation dates and places
        v += 2
        return v

    @staticmethod
    def count_unifiable_schemas(taxonomy: Taxonomy) -> int:
        v = 0
        for schema in taxonomy.entities_schemas.all():
            schema_settings = DEFAULT_ENTITIES.get(schema.name, None)
            if schema_settings is None or schema_settings["unifiable"]:
                v += 1
        return v

    def get_features_vector(self, e1: Entity, e2: Entity) -> List[float]:
        try:
            e1lv = e1.versions.filter(file_version__isnull=False).latest('id')
            e2lv = e2.versions.filter(file_version__isnull=False).latest('id')
        except EntityVersion.DoesNotExist:
            return np.abs(
                self.get_max_sim_vector(EntitySchema.objects.get(name=e1.type, taxonomy__project=e1.file.project) - 1))

        sims = self.__calculate_similarity(e1lv, e2lv)

        files_sim = self.__calculate_files_text_similarity(e1lv, e2lv)
        sims.append(files_sim)

        other_entities_sims = self.__calculate_other_entities_avg_similarity(e1lv, e2lv, files_sim)
        sims.extend(other_entities_sims)

        files_features = self.__calculate_files_creation_dates_and_places(e1lv, e2lv)
        sims.extend(files_features)

        SimilarityCache.objects.update_or_create(e1v=e1lv, e2v=e2lv, defaults={"vector": sims})

        return sims

    @staticmethod
    def get_max_sim_vector(schema: EntitySchema) -> np.ndarray:
        vec = []

        entity_settings = DEFAULT_ENTITIES.get(schema.name, None)
        properties = entity_settings['properties'] if entity_settings is not None else CUSTOM_ENTITY['properties']

        for property, params in properties.items():
            if params['type'] == TypeChoice.str:
                vec.extend([1., 0., 1., 1.])
            elif params['type'] == TypeChoice.date:
                vec.append(0.)
            elif params['type'] == TypeChoice.time:
                vec.append(0.)
            elif params['type'] == TypeChoice.Point:
                vec.append(0.)

        vec.append(1.)  # files sim

        schemas = schema.taxonomy.entities_schemas.all()
        for schema in schemas:
            schema_settings = DEFAULT_ENTITIES.get(schema.name, None)
            if schema_settings is not None and not schema_settings["unifiable"]:
                continue
            vec.append(1.)

        vec.extend([0., 0.])  # files creation dates and places
        return np.array(vec)
