import datetime
import logging
from enum import Enum
import api.config as cfg
from elasticsearch import TransportError
from schematics.models import Model
from schematics.transforms import blacklist
from schematics.types import DateTimeType, StringType, LongType
from schematics.types.compound import DictType

from api.domain.image import ImageData

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
    image_count = LongType()

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

    @property
    def csv_uri(self):
        return self.input_params.get('csv_uri', None) if self.input_params else None

    @property
    def extract_exif_annoations(self):
        return True

    @property
    def is_vision_api_enabled(self):
        return self.input_params.get('vision_api.enable', True) if self.input_params else True

    @property
    def vision_api_features(self):
        features = ['LANDMARK_DETECTION', 'LOGO_DETECTION', 'LABEL_DETECTION', 'IMAGE_PROPERTIES', 'SAFE_SEARCH_DETECTION']
        if self.input_params and 'vision_api.features' in self.input_params:
            features = self.input_params.get('vision_api.features').split(',')
        return features

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
    def __init__(self, es, index_name='cvtool'):
        self.es = es
        self.index_name = index_name

    def get_by_id(self, tenant_id, job_id):
        try:
            hit = self.es.get(index=tenant_id, id=job_id, doc_type=JobData.Meta.doc_type)
            job = JobData.from_elasticsearch(hit)
            job.image_count = self.es.count(index=tenant_id, doc_type=ImageData.Meta.doc_type).get('count')
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

    ingestion_request = dict(
        csv_uri=job_data.csv_uri,
        job_id=job_data.id,
        project_id=job_data.project_id,
        tenant_id=job_data.tenant_id
    )
    r = requests.post(url=url, json=ingestion_request)
    json = r.json()
    logger.info('Ingestion pipeline triggered: %s', json)
    return json
