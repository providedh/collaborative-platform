from django.urls import path
from . import api

urlpatterns = [
    path('upload/<int:directory_id>/', api.upload, name='upload'),
    path('<int:file_id>/versions/', api.get_file_versions, name='get_file_versions'),
    path('<int:file_id>/', api.file, name='file'),
    path('<int:file_id>/version/<int:version>/', api.get_file_version, name='get_file_version'),
    path('move/<int:move_to>', api.move, name='move'),
    path('directory/<int:directory_id>/create_subdir/<str:name>', api.create_directory, name='create_directory'),
    path('directory/<int:directory_id>', api.delete, name='delete_directory'),
    path('<int:file_id>/rename/<str:new_name>', api.rename, name='rename_file'),
    path('directory/<int:directory_id>/rename/<str:new_name>', api.rename, name='rename_directory'),
    path('get_tree/<int:project_id>', api.get_project_tree, name='get_project_tree'),
    path('<int:file_id>/download', api.download_file, name='file_download'),
    path('<int:file_id>/version/<int:version>/download/', api.download_fileversion, name='fileversion_download'),
    path('directory/<int:directory_id>/download', api.download_directory, name='directory_download'),

]
