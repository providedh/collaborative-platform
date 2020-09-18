from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

from apps.nn_disambiguator.models import Classifier
from apps.nn_disambiguator.similarity_calculator import SimilarityCalculator
from apps.projects.models import Project


def create_models(project):  # type: (Project) -> None
    schemas = project.taxonomy.entities_schemas.all()
    for entity in schemas:
        model = MLPClassifier(hidden_layer_sizes=(15, 7, 2))
        scaler = StandardScaler()

        vector = [0] * SimilarityCalculator(entity).calculate_features_vector_length(entity)
        scaler.partial_fit([vector])

        model.partial_fit([vector], [0])
        model.partial_fit([vector], [1])

        dbo = Classifier(project=project, entity_schema=entity)
        dbo.save()
        dbo.set_model(model)
        dbo.set_scaler(scaler)
