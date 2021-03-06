import traceback
from time import sleep
from typing import List
import numpy as np

from celery import shared_task
from django.core.exceptions import MultipleObjectsReturned
from django.http import JsonResponse, HttpResponse
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

from apps.api_vis.models import Entity
from apps.api_vis.request_handler import RequestHandler
from apps.nn_disambiguator.learning import learn_unprocessed
from apps.nn_disambiguator.models import Classifier, CeleryTask, UnificationProposal
from apps.nn_disambiguator.predictions import calculate_proposals
from apps.nn_disambiguator.similarity_calculator import SimilarityCalculator
from apps.projects.models import Project, ProjectVersion


@shared_task(bind=True, name='nn_disambiguator.create_models')
def create_models(self, project_id):  # type: (int) -> None
    sleep(5)
    try:
        task = CeleryTask.objects.get(project_id=project_id, task_id=self.request.id, status="S")
        task.status = "R"
        task.save()

        try:
            project = Project.objects.get(id=project_id)
            schemas = project.taxonomy.entities_schemas.all()
            for schema in schemas:
                model = MLPClassifier(hidden_layer_sizes=(15, 7, 2))
                scaler = StandardScaler()

                vector_1 = SimilarityCalculator.get_max_sim_vector(schema)
                vector_0 = np.abs(vector_1 - 1)

                scaler.partial_fit([vector_0, vector_1])
                vectors = scaler.transform([vector_0, vector_1])

                model.fit(vectors, [0, 1])
                # model.partial_fit(vectors, [0, 1], classes=[0, 1])

                dbo = Classifier(project=project, entity_schema=schema)
                dbo.save()
                dbo.set_model(model)
                dbo.set_scaler(scaler)

        except Exception:
            traceback.print_exc()
            task.status = "X"
            task.save()
        else:
            task.status = "F"
            task.save()

    except:
        traceback.print_exc()


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
        tasks = CeleryTask.objects.filter(
            project_id=project_id,
            type=type,
            status="Q"
        ).all()
        for task in tasks:
            task.status = "A"
        CeleryTask.objects.bulk_update(tasks, fields=['status'])
    except CeleryTask.DoesNotExist:
        return JsonResponse({"message": "No  pending jobs to delete"}, status=304)
    else:
        return JsonResponse({"message": "Jobs successfully aborted."})


@shared_task(name='nn_disambiguator.run_queued_tasks')
def run_queued_tasks():
    try:
        tasks = {
            "L": learn_unprocessed,
            "P": calculate_proposals,
            "C": create_models
        }

        queued_tasks = CeleryTask.objects.filter(status="Q").all()

        for task in queued_tasks:
            if CeleryTask.objects.filter(project=task.project, type=task.type, status__in=("S", "R")).exists():
                continue

            celery_task = tasks[task.type].delay(task.project_id)
            task.task_id = celery_task.task_id
            task.status = "S"
            task.save()

    except Exception as e:
        traceback.print_exc()


def serialize_unification_proposals(project_id: int, ups: List[UnificationProposal], user):
    rh = RequestHandler(project_id, user)
    pv = ProjectVersion.objects.filter(project_id=project_id).latest("id")
    result = []
    for up in ups:
        res = {"id": up.id, "degree": up.confidence, "entity": rh.serialize_entities([up.entity], pv)[0]}
        res["entity"]["file_id"] = up.entity.file_id
        res["entity"]["file_name"] = up.entity.file.name
        res["entity"]["xml:id"] = up.entity.xml_id
        if up.entity2 is not None:
            res["target_entity"] = rh.serialize_entities([up.entity2], pv)[0]
            res["target_entity"]["file_id"] = up.entity2.file_id
            res["target_entity"]["file_name"] = up.entity2.file.name
            res["target_entity"]["xml:id"] = up.entity2.xml_id
        elif up.clique is not None:
            clq = up.clique
            entities = []
            for entity in Entity.objects.filter(id__in=clq.unifications.values_list("entity_id", flat=True)):
                e = rh.serialize_entities([entity], pv)[0]
                e["file_id"] = entity.file_id
                e["file_name"] = entity.file.name
                e["xml:id"] = entity.xml_id
                entities.append(e)

            res["target_clique"] = {
                "id": clq.id,
                "name": clq.name,
                "type": clq.type,
                "entities": entities
            }
        else:
            raise KeyError("Unification proposal has no target")
        result.append(res)
    return result
