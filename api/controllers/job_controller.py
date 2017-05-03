import connexion
from swagger_server.models.job import Job
from swagger_server.models.job_step import JobStep
from swagger_server.models.new_job_request import NewJobRequest
from datetime import date, datetime
from typing import List, Dict
from six import iteritems
from ..util import deserialize_date, deserialize_datetime


def add_step(tenant_id, job_id, job_step):
    """
    add_step
    Adds an image signature to the database.
    :param tenant_id: tenant id
    :type tenant_id: str
    :param job_id: job id
    :type job_id: str
    :param job_step: job step
    :type job_step: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        job_step = JobStep.from_dict(connexion.request.get_json())
    return 'do some magic!'


def create(tenant_id, project_id, new_job_request):
    """
    create
    Adds an new job.
    :param tenant_id: tenant id
    :type tenant_id: str
    :param project_id: project id
    :type project_id: str
    :param new_job_request: new job request
    :type new_job_request: dict | bytes

    :rtype: Job
    """
    if connexion.request.is_json:
        new_job_request = NewJobRequest.from_dict(connexion.request.get_json())
    return 'do some magic!'


def end_job(tenant_id, job_id):
    """
    end_job
    Flag the job as finished
    :param tenant_id: tenant id
    :type tenant_id: str
    :param job_id: job id
    :type job_id: str

    :rtype: None
    """
    return 'do some magic!'


def get(tenant_id, job_id):
    """
    get
    Adds an image signature to the database.
    :param tenant_id: tenant id
    :type tenant_id: str
    :param job_id: job id
    :type job_id: str

    :rtype: Job
    """
    return 'do some magic!'


def start_job(tenant_id, job_id):
    """
    start_job
    Flag the job as started
    :param tenant_id: tenant id
    :type tenant_id: str
    :param job_id: job id
    :type job_id: str

    :rtype: None
    """
    return 'do some magic!'
