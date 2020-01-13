import json
from datetime import datetime
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from apps.views_decorators import objects_exists, user_has_access
from apps.projects.models import Project
from .models import Dashboard
from .forms import DashboardCreateForm, DashboardEditForm

@login_required
@objects_exists
@user_has_access('RW')
def dashboard_create(request, project_id):
    if request.method == 'POST':
        form = DashboardCreateForm(request.POST)
        project = Project.objects.get(id=project_id)

        if form.is_valid():
            new_dashboard = Dashboard(
                name = form.cleaned_data['name'], 
                description=form.cleaned_data['description'],
                project=project)
            new_dashboard.save()
            return redirect('vis_dashboard:list', project_id=project_id)
        
        return render(request, '', {form:form})

@login_required
@objects_exists
@user_has_access('RW')
def get_dashboard(request, project_id, dashboard_id):
    if request.method == 'GET':
        dashboard = Dashboard.objects.get(project_id=project_id, id=dashboard_id)
    
        context = {
            'DEVELOPMENT': True,
            'project_id': project_id,
            'dashboard_config': json.dumps(dashboard.config),
            'dashboard': dashboard
        }

        return render(request, 'vis_dashboard/dashboard.html', context)
    return redirect('vis_dashboard:list', project_id=project_id)

@login_required
@objects_exists
@user_has_access('RW')
def dashboard_edit(request, project_id, dashboard_id):
    if request.method == 'POST':
        form = DashboardEditForm(request.POST)
        
        if form.is_valid():
            dashboard = Dashboard.objects.get(project_id=project_id, id=dashboard_id)
            dashboard.name = form.cleaned_data['name']
            dashboard.description=form.cleaned_data['description']
            dashboard.save()

        return redirect('vis_dashboard:list', project_id=project_id)

@login_required
@user_has_access('RW')
def dashboard_update(request, project_id, dashboard_id):
    if request.method == 'POST':
        newConfig = json.loads(request.body.decode('UTF-8'))
        
        dashboard = Dashboard.objects.get(project_id=project_id, id=dashboard_id)
        dashboard.config = newConfig
        dashboard.last_edit = datetime.now()
        dashboard.save()

@login_required
@objects_exists
@user_has_access('RW')
def dashboard_delete(request, project_id, dashboard_id):
    if request.method == 'POST':
        dashboard = Dashboard.objects.get(project_id=project_id, id=dashboard_id)
        dashboard.delete()

    return redirect('vis_dashboard:list', project_id=project_id)

@login_required
@objects_exists
@user_has_access('RW')
def dashboard_list(request, project_id):
    if request.method == 'GET':
        create_dashboard_form = DashboardCreateForm()
        edit_dashboard_form = DashboardEditForm()
        project = Project.objects.get(id=project_id)
        dashboards = Dashboard.objects.all() \
            .filter(project_id=project_id) \
            .order_by('last_edited')

        context = {
            'project_title': project.title,
            'project_id': project_id,
            'dashboards': dashboards,
            'edit_dashboard_form': edit_dashboard_form,
            'create_dashboard_form': create_dashboard_form
        }
    
        return render(request, 'vis_dashboard/dashboard_list.html', context)