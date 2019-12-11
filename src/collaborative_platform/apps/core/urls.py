from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('settings/', views.settings, name='settings'),
    path('settings/password/', views.password, name='password'),
    path('user/<int:user_id>/', views.user, name='user'),
    path('user/', views.user, name='user_template'),
    re_path(r'^(?P<file_name>[^/]+?)$', views.static_docs, name='docs'),
]
