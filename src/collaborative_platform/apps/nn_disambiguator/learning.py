import traceback
from time import sleep

from celery import shared_task
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

from apps.api_vis.models import Entity
from apps.nn_disambiguator.similarity_calculator import SimilarityCalculator
from apps.nn_disambiguator.models import Classifier, UnificationProposal, CeleryTask
from apps.projects.models import Project
from collaborative_platform.settings import DEFAULT_ENTITIES

passes = {
    "very low": 200,
    "low": 400,
    "medium": 600,
    "high": 800,
    "very high": 1000,
    None: 1000
}


@shared_task(bind=True, name='nn_disambiguator.learn')
def learn_unprocessed(self, project_id: int):
    sleep(5)
    try:
        task = CeleryTask.objects.get(project_id=project_id, task_id=self.request.id, status="S")
        task.status = "R"
        task.save()

        try:
            project = Project.objects.get(id=project_id)
            learn_unprocessed_unifications(project)
            learn_unprocessed_proposals(project)
        except Exception:
            traceback.print_exc()
            task.status = "X"
            task.save()
        else:
            task.status = "F"
            task.save()

    except:
        traceback.print_exc()


def learn_unprocessed_unifications(project: Project):
    unlearned_unifications_exists = project.unifications.filter(learned=False).exists()
    if unlearned_unifications_exists:
        schemas = project.taxonomy.entities_schemas.all()
        for schema in schemas:
            schema_settings = DEFAULT_ENTITIES.get(schema.name, None)
            if schema_settings is not None and not schema_settings["unifiable"]:
                continue

            unifications = project.unifications.filter(learned=False,
                                                       entity__type=schema.name,
                                                       created_in_commit__isnull=False).all()
            if unifications:
                try:
                    clf = Classifier.objects.get(project_id=project.id, entity_schema=schema)
                except Classifier.DoesNotExist:
                    continue

                model: MLPClassifier = clf.get_model()
                scaler: StandardScaler = clf.get_scaler()

                data_processor = SimilarityCalculator()

                for unification in unifications:
                    entity1 = unification.entity
                    _ids = list(unification.clique.unifications.values_list("entity_id", flat=True))
                    _ids.remove(entity1.id)
                    for entity2 in Entity.objects.filter(id__in=_ids).all():
                        positive = unification.deleted_by_id is None and \
                                   unification.clique.unifications.get(entity=entity2).deleted_by_id is None
                        learn_entity_pair(entity1, entity2, data_processor, model, scaler, unification.certainty,
                                          positive)
                    unification.learned = True
                    unification.save()

                clf.set_model(model)
                clf.set_scaler(scaler)


def learn_unprocessed_proposals(project: Project):
    unlearned_decided_proposals_exists = UnificationProposal.objects.filter(entity__file__project=project, decided=True,
                                                                            learned=False).exists()
    if unlearned_decided_proposals_exists:
        schemas = project.taxonomy.entities_schemas.all()
        for schema in schemas:
            schema_settings = DEFAULT_ENTITIES.get(schema.name, None)
            if schema_settings is not None and not schema_settings["unifiable"]:
                continue

            proposals = UnificationProposal.objects.filter(entity__file__project=project, decided=True, learned=False,
                                                           entity__type=schema.name).all()

            if proposals:
                try:
                    clf = Classifier.objects.get(project_id=project.id, entity_schema=schema)
                except Classifier.DoesNotExist:
                    continue

                model: MLPClassifier = clf.get_model()
                scaler: StandardScaler = clf.get_scaler()

                data_processor = SimilarityCalculator()

                for proposal in proposals:
                    entity1 = proposal.entity
                    if proposal.clique is not None:
                        _ids = list(proposal.clique.unifications.values_list("entity_id", flat=True))
                        try:
                            _ids.remove(entity1.id)
                        except ValueError:
                            pass
                        for entity2 in Entity.objects.filter(id__in=_ids).all():
                            learn_entity_pair(entity1, entity2, data_processor, model, scaler, proposal.user_confidence,
                                              proposal.decision)
                    elif proposal.entity2 is not None:
                        learn_entity_pair(entity1, proposal.entity2, data_processor, model, scaler,
                                          proposal.user_confidence, proposal.decision)
                    proposal.learned = True
                    proposal.save()

                clf.set_model(model)
                clf.set_scaler(scaler)


def learn_entity_pair(entity1: Entity, entity2: Entity, data_processor: SimilarityCalculator,
                      model: MLPClassifier, scaler: StandardScaler,
                      user_confidence: str, positive: bool):
    positive = int(positive)
    fv = data_processor.get_features_vector(entity1, entity2)
    print(f"Schema: {entity1.type}\tvector length:\t{len(fv)}")
    scaler.partial_fit([fv])
    fv = scaler.transform([fv])
    for _ in range(passes[user_confidence]):
        model.partial_fit(fv, [positive], classes=[0, 1])
