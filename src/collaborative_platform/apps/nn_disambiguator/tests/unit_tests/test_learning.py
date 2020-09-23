import pytest
import os

from sklearn.utils.validation import check_is_fitted

from apps.api_vis.models import Entity
from apps.nn_disambiguator.learning import learn_entity_pair
from apps.nn_disambiguator.models import Classifier
from apps.nn_disambiguator.similarity_calculator import SimilarityCalculator
from apps.projects.models import EntitySchema

SCRIPT_DIR = os.path.dirname(__file__)


@pytest.mark.usefixtures('nn_disambiguator__db_setup', 'reset_db_files_directory_after_each_test')
@pytest.mark.django_db(transaction=True, reset_sequences=True)
class TestLearning:
    def test_learn_entity_pair(self):
        schema = EntitySchema.objects.get(id=1)
        data_processor = SimilarityCalculator(schema)
        e1 = Entity.objects.get(id=10)
        e2 = Entity.objects.get(id=21)
        cls = schema.classifier_set.get()
        model = cls.get_model()
        scaler = cls.get_scaler()
        user_confidence = "very high"
        positive = True

        learn_entity_pair(e1, e2, data_processor, model, scaler, user_confidence, positive)

        check_is_fitted(scaler)
        check_is_fitted(model)

        fv = data_processor.get_features_vector(e1, e2)
        fv = scaler.transform([fv])
        print(model.predict_proba(fv))
