import logging

from api.infrastructure.elasticsearch import ES, INDEX_NAME

from elasticsearch import TransportError
from schematics.models import Model
from schematics.transforms import blacklist
from schematics.types import StringType, LongType
from schematics.types.compound import DictType

logger = logging.getLogger(__name__)


class TenantData(Model):
    class Meta:
        doc_type = 'tenant'

    class Options:
        roles = {'elasticsearch': blacklist('id', 'version')}

    id = StringType()
    version = LongType()
    name = StringType()
    description = StringType()
    settings = DictType(StringType)

    @classmethod
    def from_elasticsearch(cls, raw):
        if '_source' in raw:
            data = cls(raw.get('_source'), strict=False)
            data.id = raw.get('_id')
            data.version = raw.get('_version')
        else:
            data = cls(raw, strict=False)
        return data

    @property
    def google_cloud_project(self):
        return self.settings.get('google_cloud_project')

    @property
    def staging_bucket(self):
        return self.settings.get('gcs_staging_bucket')

    def check_required_settings(self):
        if 'google_cloud_project' not in self.settings:
            raise ValueError('Missing "google_cloud_project" in tenant settings')

        if 'gcs_staging_bucket' not in self.settings:
            raise ValueError('Missing "gcs_staging_bucket" in tenant settings')

class TenantRepository(object):

    def __init__(self, es, index_name='cvtool'):
        self.es = es
        self.index_name = index_name

    def get_by_id(self, tenant_id):
        try:
            hit = self.es.get(index=self.index_name, id=tenant_id, doc_type=TenantData.Meta.doc_type)
            tenant = TenantData.from_elasticsearch(hit)
            return tenant
        except TransportError as tp:
            logger.exception('Error')
            raise tp


_tenant_repository = TenantRepository(ES, INDEX_NAME)


def get_by_id(tenant_id):
    return _tenant_repository.get_by_id(tenant_id)
