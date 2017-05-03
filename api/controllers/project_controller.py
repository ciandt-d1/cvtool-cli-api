import connexion
from swagger_server.models.project import Project
from swagger_server.models.projects import Projects
from datetime import date, datetime
from typing import List, Dict
from six import iteritems
from ..util import deserialize_date, deserialize_datetime


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
    return 'do some magic!'


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
