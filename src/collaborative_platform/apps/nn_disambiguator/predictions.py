from celery import shared_task
from numpy import average
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from typing import List, Tuple

from apps.api_vis.models import Entity, Clique, EntityVersion, Unification
from apps.nn_disambiguator.models import Classifier, UnificationProposal
from apps.nn_disambiguator.similarity_calculator import SimilarityCalculator
from apps.projects.models import Project, EntitySchema
from itertools import combinations, permutations, product


def generate_entities_pairs(schema: EntitySchema) -> List[Tuple[Entity, Entity]]:
    entities = Entity.objects.filter(type=schema.name, file__project=schema.taxonomy.project).values_list("id",
                                                                                                          flat=True)
    pairs = set(combinations(entities, 2))

    cliques = Clique.objects.filter(type=schema.name, project=schema.taxonomy.project).all()

    for clique in cliques:
        unified = clique.unifications.values_list("entity", flat=True)
        pairs.difference_update(permutations(unified, 2))

    pairs_obj = []
    for e1, e2 in pairs:
        e1o = Entity.objects.get(id=e1)
        e2o = Entity.objects.get(id=e2)
        pairs_obj.append((e1o, e2o))

    return pairs_obj


def generate_entitiy_clique_pairs(schema: EntitySchema) -> List[Tuple[Entity, Clique]]:
    entities = Entity.objects.filter(type=schema.name, file__project=schema.taxonomy.project).all()
    cliques = Clique.objects.filter(type=schema.name, project=schema.taxonomy.project).all()

    pairs = set(product(entities, cliques))

    existing_unifications = Unification.objects.filter(project=schema.taxonomy.project, clique__type=schema.name)
    existing_unifications_pairs = [(u.entitiy, u.clique) for u in existing_unifications]

    pairs.difference_update(existing_unifications_pairs)

    return list(pairs)


def calculate_entitiy_clique_sim_vector(entity: Entity, clique: Clique, data_processor: SimilarityCalculator) -> List[
    float]:
    if entity.id in clique.unifications.values_list("entity_id", flat=True):
        raise ValueError("Calculating similarity of entity with clique containing it.")

    vecs = []
    for uni in clique.unifications.all():
        vecs.append(data_processor.get_features_vector(entity, uni.entity))

    vector = list(average(vecs, axis=0))
    return vector


def make_entities_cliques_proposals(data_processor, model, scaler, schema):
    pairs = generate_entitiy_clique_pairs(schema)
    sim_vecs = [calculate_entitiy_clique_sim_vector(e, c, data_processor) for e, c in pairs]
    sim_vecs = scaler.transform(sim_vecs)
    results = [p[1] for p in model.predict_proba(sim_vecs)]
    proposals = []
    for i in range(len(pairs)):
        if results[i] > 0.7:  # TODO: make this threshold configurable?
            proposals.append((pairs[i], results[i]))
    UnificationProposal.objects.bulk_create(
        UnificationProposal(
            entity=proposal[0][0],
            clique=proposal[0][1],
            confidence=proposal[1]
        ) for proposal in proposals
    )  # TODO: test


@shared_task()
def calculate_proposals(project_id: int):
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return

    schemas = project.taxonomy.entities_schemas.all()
    for schema in schemas:
        try:
            clf = Classifier.objects.get(project_id=project.id, entity_schema=schema)
        except Classifier.DoesNotExist:
            continue

        model: MLPClassifier = clf.get_model()
        scaler: StandardScaler = clf.get_scaler()

        data_processor = SimilarityCalculator(schema)

        make_entities_proposals(data_processor, model, scaler, schema)
        make_entities_cliques_proposals(data_processor, model, scaler, schema)


def make_entities_proposals(data_processor, model, scaler, schema):
    pairs = generate_entities_pairs(schema)
    sim_vecs = [data_processor.get_features_vector(e1, e2) for e1, e2 in pairs]
    sim_vecs = scaler.transform(sim_vecs)
    results = [p[1] for p in model.predict_proba(sim_vecs)]
    proposals = []
    for i in range(len(pairs)):
        if results[i] > 0.7:  # TODO: make this threshold configurable?
            proposals.append((pairs[i], results[i]))
    UnificationProposal.objects.bulk_create(
        UnificationProposal(
            entity=proposal[0][0],
            entity2=proposal[0][1],
            confidence=proposal[1]
        ) for proposal in proposals
    )  # TODO: test
