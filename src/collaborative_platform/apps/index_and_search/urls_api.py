from django.urls import path
from . import api

urlpatterns = [
    path('entity_completion/<str:entity_type>/<str:query>/', api.entity_completion, name='entity_completion'),
]
