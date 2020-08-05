from io import BytesIO

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db.models import Model, FileField, ForeignKey, CASCADE, IntegerField, SET_NULL, CharField, BooleanField

from apps.api_vis.db_handler import DbHandler
from apps.api_vis.models import Entity, Clique
from apps.projects.models import Project, EntitySchema
import joblib


class Classifier(Model):
    project = ForeignKey(Project, on_delete=CASCADE)
    model = FileField(verbose_name="dumped model", upload_to="NN_Models", null=True)
    scaler = FileField(verbose_name="dumped scaler", upload_to="NN_Models", null=True)
    entity_schema = ForeignKey(EntitySchema, on_delete=CASCADE)

    class Meta:
        unique_together = ('project', 'entity_schema')

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


class UnificationProposal(Model):
    entity = ForeignKey(Entity, on_delete=CASCADE, related_name='e1s')
    entity2 = ForeignKey(Entity, on_delete=CASCADE, related_name='e2s', null=True)
    clique = ForeignKey(Clique, on_delete=CASCADE, related_name='proposals', null=True)
    confidence = IntegerField()

    decision_maker = ForeignKey(User, on_delete=SET_NULL, null=True, blank=True)
    user_confidence = CharField(max_length=9, null=True, blank=True)

    decided = BooleanField(default=False)
    learned = BooleanField(default=False)

    decision = BooleanField(null=True, blank=True)

    def accept(self, user, certainty, categories):
        if self.entity2 is None and self.clique is None:
            raise ValidationError("Proposal not complete")  # should never happen
        elif self.entity2 is None:
            db = DbHandler(self.entity.file.project_id, user)
            db.create_unification(self.clique, self.entity, certainty, categories,
                                  self.entity.file.project.versions.latest('id'))
            self.decision_maker = user
            self.user_confidence = certainty
            self.decided = True
            self.decision = True
            self.save()
        elif self.clique is None:
            db = DbHandler(self.entity.file.project_id, user)
            clique = db.create_clique(self.entity2.properties.filter(name='name').latest('id'), self.entity.type)
            db.create_unification(clique, self.entity, certainty, categories,
                                  self.entity.file.project.versions.latest('id'))
            # TODO: confirm with Szymon that I can unify to uncommited cliques.
            self.decision_maker = user
            self.user_confidence = certainty
            self.decided = True
            self.decision = True
            self.save()

    def reject(self, user, certainty):
        self.decision_maker = user
        self.user_confidence = certainty
        self.decided = True
        self.decision = False
        self.save()
