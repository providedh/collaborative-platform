from io import BytesIO

from django.core.files.base import ContentFile
from django.db.models import Model, FileField, ForeignKey, CASCADE
from apps.projects.models import Project, EntitySchema
import joblib


class NeuralNetwork(Model):
    project = ForeignKey(Project, on_delete=CASCADE)
    model = FileField(verbose_name="dumped model", upload_to="NN_Models", null=True)
    scaler = FileField(verbose_name="dumped scaler", upload_to="NN_Models", null=True)
    entity_type = ForeignKey(EntitySchema, on_delete=CASCADE)

    def set_model(self, model):
        bytes_container = BytesIO()
        joblib.dump(model, bytes_container)
        bytes_container.seek(0)
        file = ContentFile(bytes_container, "model.joblib")
        self.model = file
        self.save()

    def set_scaler(self, scaler):
        bytes_container = BytesIO()
        joblib.dump(scaler, bytes_container)
        bytes_container.seek(0)
        file = ContentFile(bytes_container, "scaler.joblib")
        self.scaler = file
        self.save()

    def get_model(self):
        model = joblib.load(self.model.path)
        return model

    def get_scaler(self):
        scaler = joblib.load(self.scaler.path)
        return scaler
