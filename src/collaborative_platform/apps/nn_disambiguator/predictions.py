from celery import shared_task
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from typing import List, Tuple

from apps.api_vis.models import Entity, Clique, EntityVersion
from apps.nn_disambiguator.models import Classifier, UnificationProposal
from apps.nn_disambiguator.similarity_calculator import SimilarityCalculator
from apps.projects.models import Project, EntitySchema
from itertools import combinations, permutations


def generate_pairs(schema: EntitySchema) -> List[Tuple[Entity, Entity]]:
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


@shared_task()
def calculate_proposals(project_id: int):
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return

    schemas = project.taxonomy.entities_schemas.all()
    for schema in schemas:
        pairs = generate_pairs(schema)

        try:
            clf = Classifier.objects.get(project_id=project.id, entity_schema=schema)
        except Classifier.DoesNotExist:
            continue

        model: MLPClassifier = clf.get_model()
        scaler: StandardScaler = clf.get_scaler()

        data_processor = SimilarityCalculator(schema)

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
