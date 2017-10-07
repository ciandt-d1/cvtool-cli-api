import logging
import json

from elasticsearch import helpers
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
    similar = StringType()

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

    def add_annotations(self, tenant_id, id_versions, annotations):
        query = {
            "script": {
                "inline": "ctx._source.annotations.putAll(params.annotations)",
                "params": {
                    "annotations": annotations
                }
            }
        }
        self._bulk_update_indexed_image(tenant_id, id_versions, query)

    def remove_annotations(self, tenant_id, id_versions, annotations):
        query = {
            "script": {
                "inline": "ctx._source.annotations.keySet().removeAll(params.keys)",
                "params": {
                    "keys": annotations.keys()
                }
            }
        }
        self._bulk_update_indexed_image(tenant_id, id_versions, query)

    def get_by_original_uri(self, tenant_id, original_uri):

        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"original_uri.raw": original_uri}}
                    ]
                }
            }
        }

        hit = self.es.search(index=tenant_id, doc_type=ImageData.Meta.doc_type, size=1, version=True,
                             body=query)
        if hit['hits']['total'] == 0:
            image = None
        else:
            image = ImageData.from_elasticsearch(hit['hits']['hits'][0])

        return image

    def get_all(self, tenant_id, offset=0, limit=100):
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

    def search(self, tenant_id, query, offset=0, limit=100):
        final_query = {
            'query': {
                'bool': {
                    'filter': [
                        {
                            'type': {
                                'value': ImageData.Meta.doc_type
                            }
                        }
                    ]
                }
            }
        }
        valid_clause = ['must', 'must_not', 'should']
        query_dict = json.loads(query)
        query_bool_dict = query_dict.get('query', {}).get('bool', {})
        for k, v in query_bool_dict.items():
            if k in valid_clause:
                final_query.get('query', {}).get('bool', {}).update({k: v})
        source_include = query_dict.get('_source',
                                         ['tenant_id', 'job_id', 'uri', 'height', 'width', 'size', 'similar',
                                          'annotations'])
        try:
            result = self.es.search(index=tenant_id, doc_type=ImageData.Meta.doc_type,
                                    from_=offset, size=limit, body=final_query,
                                    _source_include=source_include, version=True)
            total = result['hits']['total']
            if total == 0:
                image_list = []
            else:
                image_list = [ImageData.from_elasticsearch(hit) for hit in result['hits']['hits']]
            return total, image_list
        except TransportError as tp:
            logger.exception('Error')
            raise tp

    def _bulk_update_indexed_image(self, tenant_id, id_versions, query):
        actions = []
        for k, v in id_versions.items():
            action = {
                '_op_type': 'update',
                '_index': tenant_id,
                '_type': ImageData.Meta.doc_type,
                '_id': k,
                '_source': query,
                '_version': v
            }
            actions.append(action)
        if actions:
            helpers.bulk(self.es, actions)


