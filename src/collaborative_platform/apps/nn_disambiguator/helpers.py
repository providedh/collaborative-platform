from celery import shared_task
from django.core.exceptions import MultipleObjectsReturned
from django.http import JsonResponse, HttpResponse
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

from apps.api_vis.request_handler import RequestHandler
from apps.nn_disambiguator.learning import learn_unprocessed
from apps.nn_disambiguator.models import Classifier, CeleryTask
from apps.nn_disambiguator.predictions import calculate_proposals
from apps.nn_disambiguator.similarity_calculator import SimilarityCalculator
from apps.projects.models import Project, ProjectVersion


def create_models(project):  # type: (Project) -> None
    schemas = project.taxonomy.entities_schemas.all()
    for entity in schemas:
        model = MLPClassifier(hidden_layer_sizes=(15, 7, 2))
        scaler = StandardScaler()

        vector = [0] * SimilarityCalculator(entity).calculate_features_vector_length(entity)
        scaler.partial_fit([vector])

        model.partial_fit([vector], [0], classes=[0, 1])
        model.partial_fit([vector], [1], classes=[0, 1])

        dbo = Classifier(project=project, entity_schema=entity)
        dbo.save()
        dbo.set_model(model)
        dbo.set_scaler(scaler)


def queue_task(project_id: int, type: str):
    try:
        CeleryTask.objects.get_or_create(
            project_id=project_id,
            type=type,
            status="Q"
        )
    except MultipleObjectsReturned:
        pass

    return HttpResponse()


def abort_pending(project_id: int, type: str):
    try:
        CeleryTask.objects.filter(
            project_id=project_id,
            type=type,
            status="Q"
        ).delete()
    except CeleryTask.DoesNotExist:
        return JsonResponse({"message": "No  pending jobs to delete"}, status=304)
    else:
        return JsonResponse({"message": "Jobs successfully aborted."})


@shared_task(name='nn_disambiguator.run_queued_tasks')
def run_queued_tasks():
    tasks = {
        "L": learn_unprocessed,
        "P": calculate_proposals
    }

    queued_tasks = CeleryTask.objects.filter(status="Q").all()

    for task in queued_tasks:
        celery_task = tasks[task.type].delay(task.project_id)
        task.task_id = celery_task.task_id
        task.status = "S"
        task.save()

# @shared_task(name="clean_unfinished_tasks")
# def clean_unfinished_tasks():
def serialize_unification_proposals(project_id: int, ups, user):
    rh = RequestHandler(project_id, user)
    pv = ProjectVersion.objects.filter(project_id=project_id).latest("id")
    result = []
    for up in ups:
        res = {"id": up.id, "degree": up.confidence, "entity": rh.serialize_entities([up.entity], pv)[0]}
        if up.entity2 is not None:
            res["target_entity"] = rh.serialize_entities([up.entity2], pv)[0]
        elif up.clique is not None:
            clq = up.clique
            res["target_clique"] = {
                "id": clq.id,
                "name": clq.name,
                "type": clq.type,
                "entities": clq.unifications.values_list("entity_id", flat=True)
            }
        else:
            raise KeyError("Unification proposal has no target")
        result.append(res)
    return result
