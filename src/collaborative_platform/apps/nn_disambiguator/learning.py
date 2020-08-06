from celery import shared_task
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

from apps.api_vis.models import Entity
from apps.nn_disambiguator.data_processor import DataProcessor
from apps.nn_disambiguator.models import Classifier, UnificationProposal
from apps.projects.models import Project

passes = {
    "very low": 20,
    "low": 40,
    "medium": 60,
    "high": 80,
    "very high": 100
}


@shared_task()
def learn_unprocessed(project_id: int):
    # unifications
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return

    learn_unprocessed_unifications(project)
    learn_unprocessed_proposals(project)


def learn_unprocessed_unifications(project: Project):
    unlearned_unifications_exists = project.unifications.filter(learned=False).exists()
    if unlearned_unifications_exists:
        schemas = project.taxonomy.entities_schemas.all()
        for schema in schemas:
            unifications = project.unifications.filter(learned=False, entitiy__type=schema.name).all()
            if unifications:
                try:
                    clf = Classifier.objects.get(project_id=project.id, entity_schema=schema)
                except Classifier.DoesNotExist:
                    continue

                model: MLPClassifier = clf.get_model()
                scaler: StandardScaler = clf.get_scaler()

                data_processor = DataProcessor(schema)

                for unification in unifications:
                    entity1 = unification.entity
                    _ids = list(unification.clique.unifications.values_list("entity_id", flat=True))
                    _ids.remove(entity1.id)
                    for entity2 in Entity.objects.filter(id__in=_ids).all():
                        learn_entity_pair(entity1, entity2, data_processor, model, scaler, unification.certainty, 1)

                clf.set_model(model)
                clf.set_scaler(scaler)


def learn_unprocessed_proposals(project):
    unlearned_decided_proposals_exists = UnificationProposal.objects.filter(entity__file__project=project, decided=True,
                                                                            learned=False).exists()
    if unlearned_decided_proposals_exists:
        schemas = project.taxonomy.entities_schemas.all()
        for schema in schemas:
            proposals = UnificationProposal.objects.filter(entity__file__project=project, decided=True, learned=False,
                                                           entity__type=schema.name).all()

            if proposals:
                try:
                    clf = Classifier.objects.get(project_id=project.id, entity_schema=schema)
                except Classifier.DoesNotExist:
                    continue

                model: MLPClassifier = clf.get_model()
                scaler: StandardScaler = clf.get_scaler()

                data_processor = DataProcessor(schema)

                for proposal in proposals:
                    entity1 = proposal.entity
                    if proposal.clique is not None:
                        _ids = list(proposal.clique.unifications.values_list("entity_id", flat=True))
                        _ids.remove(entity1.id)
                        for entity2 in Entity.objects.filter(id__in=_ids).all():
                            learn_entity_pair(entity1, entity2, data_processor, model, scaler, proposal.user_confidence,
                                              proposal.decision)
                    elif proposal.entity2 is not None:
                        learn_entity_pair(entity1, proposal.entity2, data_processor, model, scaler,
                                          proposal.user_confidence, proposal.decision)


def learn_entity_pair(entity1, entity2, data_processor, model, scaler, user_confidence, positive):
    positive = int(positive)
    fv = data_processor.get_features_vector(entity1, entity2)
    scaler.partial_fit(fv)
    fv = scaler.transform(fv)
    for _ in range(passes[user_confidence]):
        model.partial_fit(fv, [positive], classes=[0, 1])
