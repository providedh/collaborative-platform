from django.urls import path
from src.apps.core import views

urlpatterns = [
    path('', views.index, name='index'),
]
