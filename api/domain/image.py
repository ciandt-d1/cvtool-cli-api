import logging

from elasticsearch import TransportError
from schematics.models import Model
from schematics.transforms import blacklist
from schematics.types import StringType, LongType
from schematics.types.compound import DictType

logger = logging.getLogger(__name__)


class ImageData(Model):
    class Meta:
        doc_type = 'image'

    class Options:
        roles = {'elasticsearch': blacklist('id', 'version')}

    id = StringType()
    version = LongType()
    tenant_id = StringType()
    job_id = StringType()
    original_uri = StringType()
    annotations = DictType(StringType)
    exif_annotations = DictType(StringType)
    vision_annotations = StringType()

    @classmethod
    def from_elasticsearch(cls, raw):
        if '_source' in raw:
            data = cls(raw.get('_source'), strict=False)
            data.id = raw.get('_id')
            data.version = raw.get('_version')
            data.tenant_id = raw.get('_routing')
        else:
            data = cls(raw, strict=False)
        return data


class ImageRepository(object):

    def __init__(self, es, index_name='cvtool'):
        self.es = es
        self.index_name = index_name

    def get_by_id(self, tenant_id, id):
        try:
            hit = self.es.get(index=tenant_id, id=id, doc_type=ImageData.Meta.doc_type)
            image = ImageData.from_elasticsearch(hit)
            return image
        except TransportError as tp:
            logger.exception('Error')

    def get_by_original_uri(self, tenant_id, original_uri):

        query = {
            'query': {
                {'term': {'original_uri.raw': original_uri}}
            }
        }

        try:
            hit = self.es.search(index=tenant_id, doc_type=ImageData.Meta.doc_type, size=1, version=True,
                                 body=query)
            if hit['hits']['total'] == 0:
                image = None
            else:
                image = ImageData.from_elasticsearch(hit['hits']['hits'][0])

            return image
        except TransportError as tp:
            logger.exception('Error')

    def get_all(self, tenant_id, project_id=None, offset=0, limit=100):
        try:
            result = self.es.search(index=tenant_id, doc_type=ImageData.Meta.doc_type, from_=offset, size=limit, version=True)
            total = result['hits']['total']
            if total == 0:
                image_list = []
            else:
                image_list = [ImageData.from_elasticsearch(hit) for hit in result['hits']['hits']]

            return total, image_list


        except TransportError as tp:
            logger.exception('Error')
            raise tp

    def save(self, tenant_id, image):
        try:
            image.tenant_id = tenant_id
            result = self.es.index(index=image.tenant_id, doc_type=ImageData.Meta.doc_type,
                                   body=image.to_primitive(role='elasticsearch'))
            image.id = result.get('_id')
            image.version = result.get('_version')
            return image
        except TransportError as tp:
            logger.exception('Error')
            raise tp
