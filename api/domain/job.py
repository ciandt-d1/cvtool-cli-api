import datetime
import logging
from enum import Enum
import api.config as cfg
from elasticsearch import TransportError
from schematics.models import Model
from schematics.transforms import blacklist
from schematics.types import DateTimeType, StringType, LongType
from schematics.types.compound import DictType

logger = logging.getLogger(__name__)


class JobType(Enum):
    csv = 1
    flickr = 2


class JobStatus(Enum):
    CREATED = 1
    RUNNING = 2
    FINISHED = 3


class JobData(Model):
    class Meta:
        doc_type = 'job'

    class Options:
        roles = {'elasticsearch': blacklist('id', 'version')}

    id = StringType()
    version = LongType()
    tenant_id = StringType(required=True)
    project_id = StringType()
    job_type = StringType(required=True, choices=[type.name for type in JobType], default=JobType.csv.name)
    status = StringType(required=True, choices=[status.name for status in JobStatus], default=JobStatus.CREATED.name)
    exit_status = StringType()
    exit_message = StringType()
    create_time = DateTimeType(default=datetime.datetime.now)
    start_time = DateTimeType()
    end_time = DateTimeType()
    last_updated = DateTimeType(default=datetime.datetime.now)
    created_by = StringType()
    input_params = DictType(StringType)

    def start(self):
        if self.status != JobStatus.CREATED.name:
            raise AttributeError('Cannot start job in status ' + self.status)

        self.status = JobStatus.RUNNING.name
        self.start_time = datetime.datetime.now()
        self.last_updated = self.start_time

    def end(self):
        if self.status != JobStatus.RUNNING.name:
            raise AttributeError('Cannot end job in status ' + self.status)

        self.status = JobStatus.FINISHED.name
        self.end_time = datetime.datetime.now()
        self.last_updated = self.end_time

    def __str__(self):
        return 'JobData(id={id})'.format(id=self.id)

    @classmethod
    def from_elasticsearch(cls, raw):
        if '_source' in raw:
            job_data = cls(raw.get('_source'), strict=False)
            job_data.id = raw.get('_id')
            job_data.version = raw.get('_version')
            job_data.tenant_id = raw.get('_routing')
        else:
            job_data = cls(raw, strict=False)
        return job_data


class JobRepository(object):
    def __init__(self, es, index_name='kingpick'):
        self.es = es
        self.index_name = index_name

    def get_by_id(self, tenant_id, job_id):
        try:
            hit = self.es.get(index=tenant_id, id=job_id, doc_type=JobData.Meta.doc_type)
            job = JobData.from_elasticsearch(hit)
            return job
        except TransportError as tp:
            logger.exception('Error')
            raise tp

    def get_all(self, tenant_id, offset=0, limit=100):
        try:
            result = self.es.search(index=tenant_id, doc_type=JobData.Meta.doc_type, from_=offset, size=limit,
                                    version=True)
            job = JobData(result)
            return job
        except TransportError as tp:
            logger.exception('Error')
            raise tp

    def save(self, job):
        try:
            result = self.es.index(index=job.tenant_id, doc_type=JobData.Meta.doc_type,
                                   body=job.to_primitive(role='elasticsearch'), id=job.id, version=job.version)
            job.id = result.get('_id')
            job.version = result.get('_version')
            return job
        except TransportError as tp:
            logger.exception('Error')
            raise tp

    def add_step(self, tenant_id, step):
        raise NotImplementedError()
        # try:
        #     self.create(index=tenant_id, doc_type=JobData.Meta.doc_type, id=step.id, body=step.flatten())
        #     return job
        # except TransportError as tp:
        #     logger.exception('Error')


def trigger_csv_ingestion(job_data):
    import requests

    # {
    #     "ingestion_request": {
    #         "csv_uri": "/bucket/costarica-moths/input.csv",
    #         "job_id": "AVvaFoMsrwRXigckTEVd",
    #         "project_id": "project-x",
    #         "tenant_id": "acme"
    #     },
    #     "pipeline_id": "AVvaFoMsrwRXigckTEVd",
    #     "pipeline_results_uri": "/mapreduce/pipeline/status?root=AVvaFoMsrwRXigckTEVd"
    # }

    url = cfg.IMAGE_INGESTION_PIPELINE_URI
    r = requests.post(url=url, json=job_data)
    json = r.json()
    logger.info('Ingestion pipeline triggered: %s', json)
    return json
