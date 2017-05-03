import datetime
import json
import logging
from enum import Enum

from elasticsearch import Elasticsearch, TransportError
from schematics.models import Model
from schematics.transforms import blacklist
from schematics.types import DateTimeType, StringType, URLType, LongType
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
        roles = {'public': blacklist('id')}

    id = StringType()
    version = LongType()
    tenant_id = StringType(required=True)
    project_id = StringType()
    job_type = StringType(required=True, choices=[type.name for type in JobType], default=JobType.csv.name)
    status = StringType(required=True, choices=[status.name for status in JobStatus],  default=JobStatus.CREATED.name)
    exit_status = StringType()
    exit_message = StringType()
    create_time = DateTimeType(default=datetime.datetime.now)
    start_time = DateTimeType()
    end_time = DateTimeType()
    last_updated = DateTimeType(default=datetime.datetime.now)
    created_by = StringType()
    input_params = DictType(StringType)

    def start(self):
        self.status = JobStatus.RUNNING.name
        self.start_time = datetime.datetime.now
        self.last_updated = self.start_time

    def end(self):
        self.status = JobStatus.FINISHED.name
        self.end_time = datetime.datetime.now
        self.last_updated = self.end_time


class JobRepository(object):
    
    def __init__(self, es, index_name='kingpick'):
        self.es = es
        self.index_name = index_name

    def get_by_id(self, tenant_id, id):
        try:
            hit = self.es.get(index=tenant_id, id=id, doc_type=JobData.Meta.doc_type)
            job = JobData(hit)
            return job
        except TransportError as tp:
            logger.exception('Error')

    def get_all(self, tenant_id, offset=0, limit=100):
        try:
            result = self.es.search(index=tenant_id, doc_type=JobData.Meta.doc_type, from_=offset, size=limit, version=True)
            job = JobData(hit)
            return job
        except TransportError as tp:
            logger.exception('Error')

    def save(self, tenant_id, project_id, job):
        try:
            result = self.es.index(index=tenant_id, doc_type=JobData.Meta.doc_type, body=job.to_primitive())
            job.id = result.get('_id')
            job.version = result.get('_version')
            return job
        except TransportError as tp:
            logger.exception('Error')
            raise tp

    def add_step(self, tenant_id, step):
        try:
            self.create(index=tenant_id, doc_type=JobData.Meta.doc_type, id=step.id, body=step.flatten())
            return job
        except TransportError as tp:
            logger.exception('Error')
