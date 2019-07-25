from django.urls import path
from . import api

urlpatterns = [
    path('upload/', api.upload, name='upload'),
]
