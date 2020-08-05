from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

from apps.nn_disambiguator.models import Classifier
from apps.projects.models import Project


def create_models(project):  # type: (Project) -> None
    schemas = project.taxonomy.entities_schemas.all()
    for entitiy in schemas:
        model = MLPClassifier(hidden_layer_sizes=(15, 7, 2))
        scaler = StandardScaler()

        dbo = Classifier(project, entity_type=entitiy)
        dbo.save()
        dbo.set_model(model)
        dbo.set_scaler(scaler)
