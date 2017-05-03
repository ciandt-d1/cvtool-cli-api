import logging

from datetime import date, datetime
from typing import Dict, List

import connexion
from elasticsearch import Elasticsearch, TransportError
from six import iteritems

from api.representations.job import Job
from api.representations.job_step import JobStep
from api.representations.new_job_request import NewJobRequest

from ..domain.job import JobData, JobRepository
from ..util import deserialize_date, deserialize_datetime

logger = logging.getLogger(__name__)

INDEX_NAME = 'kingpick'
ES = Elasticsearch('http://elasticsearch:9200')
job_repository = JobRepository(ES, INDEX_NAME)

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
        job = JobData(new_job_request, strict=False)
        job = job_repository.save(tenant_id, project_id, job)

    return Job.from_dict(job.flatten())


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
