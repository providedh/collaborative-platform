from django.urls import path
from . import api

urlpatterns = [
    path('upload/', api.upload, name='upload'),
    path('<int:file_id>/versions/', api.get_file_versions, name='get_file_versions'),
    path('<int:file_id>/', api.get_file_version, name='get_file'),
    path('<int:file_id>/version/<int:version>/', api.get_file_version, name='get_file_version'),
    path('move/file/<int:file_id>/<int:move_to>', api.move, name='move_file'),
    path('move/directory/<int:directory_id>/<int:move_to>', api.move, name='move_directory'),
    path('create/directory/<int:directory_id>/<str:name>', api.create_directory, name='create_directory'),
    path('file/<int:file_id>', api.delete, name='delete_file'),
    path('directory/<int:directory_id>', api.delete, name='delete_directory'),
    path('rename/file/<int:file_id>/<str:new_name>', api.rename, name='rename_file'),
    path('rename/directory/<int:directory_id>/<str:new_name>', api.rename, name='rename_directory'),
    path('get_tree/<int:project_id>', api.get_project_tree, name='get_project_tree'),
    path('<int:file_id>/download', api.download_file, 'file_download'),
    path('<int:file_id>/version/<int:version_number>/download', api.download_fileversion, 'fileversion_download'),
]
