import logging

from elasticsearch import TransportError
from schematics.models import Model
from schematics.transforms import blacklist
from schematics.types import StringType
from schematics.types.compound import DictType

logger = logging.getLogger(__name__)


class ImageData(Model):
    class Meta:
        doc_type = 'image'

    class Options:
        roles = {'public': blacklist('id')}

    id = StringType()
    job_id = StringType()
    original_uri = StringType()
    annotations = DictType(StringType)


class ImageRepository(object):
    
    def __init__(self, es, index_name='kingpick'):
        self.es = es
        self.index_name = index_name

    def get_by_id(self, tenant_id, id):
        try:
            hit = self.es.get(index=tenant_id, id=id, doc_type=ImageData.Meta.doc_type)
            image = ImageData(hit)
            return image
        except TransportError as tp:
            logger.exception('Error')

    def get_by_original_uri(self, tenant_id, original_uri):
        try:
            hit = self.es.search(index=tenant_id, doc_type=ImageData.Meta.doc_type, size=1,
                                 body='{"field" : {"original_uri" : ' + original_uri + '}}')
            image = ImageData(hit)
            return image
        except TransportError as tp:
            logger.exception('Error')

    def get_all(self, tenant_id, offset=0, limit=100):
        try:
            result = self.es.search(index=tenant_id, doc_type=ImageData.Meta.doc_type, from_=offset, size=limit, version=True)
            image = ImageData(result)
            return image
        except TransportError as tp:
            logger.exception('Error')

    def save(self, tenant_id, project_id, image):
        try:
            result = self.es.index(index=tenant_id, doc_type=ImageData.Meta.doc_type, body=image.to_primitive())
            image.id = result.get('_id')
            image.version = result.get('_version')
            return image
        except TransportError as tp:
            logger.exception('Error')
            raise tp
