import connexion

from api.infrastructure.elasticsearch import ES, PROJECT_DOC_TYPE
from api.representations.project import Project
from api.representations.projects import Projects


def create_project(tenant_id, project):
    """
    Creates a new project
    Creates a new project return the project.
    :param tenant_id: tenant id
    :type tenant_id: str
    :param project: Project to create
    :type project: dict | bytes

    :rtype: Project
    """
    if connexion.request.is_json:
        project_json = connexion.request.get_json()
        project = Project.from_dict(project_json)
        project_dict = project.to_dict()
        project_dict['tenant_id'] = tenant_id
        ES.create(index=tenant_id, doc_type='project', id=project.id, body=project_dict)
        return project, 201


def put_project(tenant_id, project_id, project):
    """
    put_project
    updates a project
    :param tenant_id: tenant id
    :type tenant_id: str
    :param project_id: project id
    :type project_id: str
    :param project: Project to update
    :type project: dict | bytes

    :rtype: Project
    """
    if connexion.request.is_json:
        project = Project.from_dict(connexion.request.get_json())
    return 'do some magic!'


def get_project(tenant_id, project_id):
    """
    get_project
    get a specific project
    :param tenant_id: tenant id
    :type tenant_id: str
    :param project_id: project id
    :type project_id: str

    :rtype: Project
    """
    return 'do some magic!'


def list_projects(tenant_id):
    """
    list_projects
    List all projects
    :param tenant_id: tenant id
    :type tenant_id: str

    :rtype: Projects
    """
    hits = ES.search(index=tenant_id, doc_type=PROJECT_DOC_TYPE, version=True)
    projects = list(map(lambda hit: Project.from_dict(hit.get('_source')), hits.get('hits', {'hits': []}).get('hits')))
    return Projects(items=projects)
