from apps.projects.models import Project, ProjectVersion


def get_project_versions(project_id: int):
    def get_pv_author(pv):
        file_versions = pv.file_versions.all()
        return 'system' if len(file_versions) == 0 else file_versions[0].created_by.username

    try:
        project_versions = Project.objects\
            .get(pk=project_id).versions.all()\
            .order_by('id')

        pv_data = lambda pv: {'version': str(pv),
                              'date': pv.date,
                              'author': get_pv_author(pv)}
        history = [pv_data(pv) for pv in project_versions]
        return history
    except Exception as e:
        print(e)
        return []