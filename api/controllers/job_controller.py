import logging
import tempfile
import uuid

import connexion
from google.cloud._helpers import _to_bytes

from api.representations import NewJobRequest, Job, JobStep
from ..domain.job import JobData, JobRepository, trigger_csv_ingestion
from ..infrastructure.elasticsearch import ES, INDEX_NAME
from google.cloud import storage

logger = logging.getLogger(__name__)
job_repository = JobRepository(ES, INDEX_NAME)


def generate_input_csv(bucket_path):
    bucket_name = bucket_path.split('/', 3)[2]
    prefix = bucket_path.split('/', 3)[3]

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)

    file_name = str(uuid.uuid4())
    output_blob = storage.Blob('csv/{export_id}.csv'.format(export_id=file_name), bucket)

    blobs = bucket.list_blobs(prefix=prefix, delimiter='/')

    with tempfile.NamedTemporaryFile() as tmp_file:
        tmp_file.write(_to_bytes('file\n', encoding='utf-8'))
        for item in blobs:
            tmp_file.write(_to_bytes('gs://' + bucket_name + '/' + item.name + '\n', encoding='utf-8'))
        output_blob.upload_from_file(tmp_file, client=storage_client, rewind=True)

    return 200, 'gs://{bucket_name}/csv/{export_id}.csv'.format(bucket_name=bucket_name, export_id=file_name)


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
        job_representation = NewJobRequest.from_dict(new_job_request)
        job = JobData(new_job_request, strict=False)
        job.tenant_id = tenant_id
        job.project_id = project_id
        job = job_repository.save(job)

        if job_representation.auto_start:
            try:
                trigger_csv_ingestion(job)
            except:
                logger.exception('Could not trigger pipeline ingestion.')

        flattened_job = job.flatten()
        return Job.from_dict(flattened_job)


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

    job = job_repository.get_by_id(tenant_id, job_id)
    job.end()
    job = job_repository.save(job)
    return Job.from_dict(job.flatten())


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
    job = job_repository.get_by_id(tenant_id, job_id)
    logger.info(str(job.flatten()))
    job_model = Job.from_dict(job.flatten())
    return job_model


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

    job = job_repository.get_by_id(tenant_id, job_id)
    job.start()
    job = job_repository.save(job)
    return Job.from_dict(job.flatten())


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
