from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create, name='create'),
    path('get_public/', views.get_public, name='get_public'),
]
