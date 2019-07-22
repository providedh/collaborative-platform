from django.urls import path
# from src.collaborative_platform.apps.core import views

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
]
