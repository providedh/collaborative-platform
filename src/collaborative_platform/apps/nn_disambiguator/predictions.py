import traceback
from time import sleep, strftime

from celery import shared_task
from numpy import average
from sklearn.exceptions import NotFittedError
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.utils.validation import check_is_fitted
from typing import List, Tuple

from apps.api_vis.models import Entity, Clique, Unification
from apps.files_management.models import File
from apps.nn_disambiguator.models import Classifier, UnificationProposal, CeleryTask
from apps.nn_disambiguator.similarity_calculator import SimilarityCalculator
from apps.projects.models import Project, EntitySchema
from itertools import combinations, permutations, product

from collaborative_platform.settings import DEFAULT_ENTITIES


def log(text):
    print(f"{strftime('%H:%M:%S')}: {text}")


def generate_entities_pairs(schema: EntitySchema) -> List[Tuple[Entity, Entity]]:
    entities = Entity.objects.filter(type=schema.name, file__project=schema.taxonomy.project).values_list("id",
                                                                                                          flat=True)
    pairs = set(combinations(entities, 2))

    cliques = Clique.objects.filter(type=schema.name, project=schema.taxonomy.project,
                                    created_in_commit__isnull=False).all()

    for clique in cliques:
        unified = clique.unifications.values_list("entity", flat=True)
        pairs.difference_update(permutations(unified, 2))

    for file in File.objects.filter(project=schema.taxonomy.project, deleted=False).all():
        pairs.difference_update(permutations(file.entity_set.values_list("id", flat=True), 2))

    pairs_obj = []
    for e1, e2 in pairs:
        e1o = Entity.objects.get(id=e1)
        e2o = Entity.objects.get(id=e2)
        pairs_obj.append((e1o, e2o))

    return pairs_obj


def generate_entity_clique_pairs(schema: EntitySchema) -> List[Tuple[Entity, Clique]]:
    entities = Entity.objects.filter(type=schema.name, file__project=schema.taxonomy.project).all()
    cliques = Clique.objects.filter(type=schema.name, project=schema.taxonomy.project,
                                    created_in_commit__isnull=False).all()

    pairs = set(product(entities, cliques))

    existing_unifications = Unification.objects.filter(project=schema.taxonomy.project, clique__type=schema.name,
                                                       created_in_commit__isnull=False)
    existing_unifications_pairs = [(u.entity, u.clique) for u in existing_unifications]

    pairs.difference_update(existing_unifications_pairs)

    return list(pairs)


def calculate_entity_clique_sim_vector(entity: Entity, clique: Clique, data_processor: SimilarityCalculator) -> List[
    float]:
    if entity.id in clique.unifications.values_list("entity_id", flat=True):
        raise ValueError("Calculating similarity of entity with clique containing it.")

    vecs = []
    for uni in clique.unifications.all():
        vecs.append(data_processor.get_features_vector(entity, uni.entity))

    vector = list(average(vecs, axis=0))
    return vector


def make_entities_cliques_proposals(data_processor, model, scaler, schema):
    pairs = generate_entity_clique_pairs(schema)
    log("Generated pairs")

    for e, c in pairs:
        sim_vec = calculate_entity_clique_sim_vector(e, c, data_processor)
        log("Got sims vector")
        sim_vec = scaler.transform([sim_vec])
        p = model.predict_proba(sim_vec)[0][1]

        log(f"Predicted. p={p}")

        if p >= 0.0:  # TODO: make this threshold configurable?
            UnificationProposal(
                entity=e,
                clique=c,
                confidence=p * 100
            ).save()
            log("Saved")


def make_entities_proposals(data_processor, model, scaler, schema):
    pairs = generate_entities_pairs(schema)
    log("Generated pairs")

    for e1, e2 in pairs:
        sim_vec = data_processor.get_features_vector(e1, e2)
        log("Got sims vector")
        sim_vec = scaler.transform([sim_vec])
        p = model.predict_proba(sim_vec)[0][1]

        log(f"Predicted. p={p}")

        if p >= 0.0:
            UnificationProposal(
                entity=e1,
                entity2=e2,
                confidence=p * 100
            ).save()
            log("Saved")


def reset_undecided_proposals(project_id: int):
    try:
        proposals = UnificationProposal.objects.filter(entity__file__project_id=project_id, decided=False)
    except UnificationProposal.DoesNotExist:
        return

    proposals.delete()


@shared_task(bind=True, name='nn_disambiguator.predict')
def calculate_proposals(self, project_id: int):
    sleep(5)
    try:
        task = CeleryTask.objects.get(project_id=project_id, task_id=self.request.id, status="S")
        task.status = "R"
        task.save()
        log("Proposals task ran")

        try:
            project = Project.objects.get(id=project_id)

            reset_undecided_proposals(project_id)
            log("Proposals reset")

            schemas = project.taxonomy.entities_schemas.all()
            for schema in schemas:
                schema_settings = DEFAULT_ENTITIES.get(schema.name, None)
                if schema_settings is not None and not schema_settings["unifiable"]:
                    continue

                try:
                    clf = Classifier.objects.get(project_id=project.id, entity_schema=schema)
                except Classifier.DoesNotExist:
                    continue

                model: MLPClassifier = clf.get_model()
                scaler: StandardScaler = clf.get_scaler()

                try:
                    check_is_fitted(model)
                    check_is_fitted(scaler)
                except NotFittedError:
                    continue

                data_processor = SimilarityCalculator()

                make_entities_proposals(data_processor, model, scaler, schema)
                make_entities_cliques_proposals(data_processor, model, scaler, schema)

            task.status = "F"
            task.save()

        except:
            traceback.print_exc()
            task.status = "X"
            task.save()
            return

    except:
        traceback.print_exc()
