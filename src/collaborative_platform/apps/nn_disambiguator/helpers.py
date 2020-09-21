from celery import shared_task
from django.core.exceptions import MultipleObjectsReturned
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

from apps.nn_disambiguator.learning import learn_unprocessed
from apps.nn_disambiguator.models import Classifier, CeleryTask
from apps.nn_disambiguator.predictions import calculate_proposals
from apps.nn_disambiguator.similarity_calculator import SimilarityCalculator
from apps.projects.models import Project


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
