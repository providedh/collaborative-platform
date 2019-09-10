from django.urls import path
from . import api

urlpatterns = [
    path('create/', api.create, name='create'),
    path('get_public/', api.get_public, name='get_public'),
    path('get_mine/', api.get_mine, name='get_mine'),
    path('get_users/<int:user_id>/', api.get_users, name='get_users'),
    path('<int:project_id>/activities/', api.get_activities, name='activities'),
    path('<int:project_id>/make_public', api.make_public, name='make_public'),
    path('<int:project_id>/make_private', api.make_private, name='make_private')
]
