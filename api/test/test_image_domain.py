# coding: utf-8

from __future__ import absolute_import

import logging
import unittest

from api.domain.image import ImageData

logger = logging.getLogger(__name__)

ES_JSON_RESPONSE = {
  "took": 15,
  "timed_out": False,
  "_shards": {
    "total": 10,
    "successful": 10,
    "failed": 0
  },
  "hits": {
    "total": 1,
    "max_score": 7.3399706,
    "hits": [
      {
        "_index": "cvtool",
        "_type": "image",
        "_version": 1,
        "_id": "AVvaFxxcrwRXigckTEVk",
        "_score": 7.3399706,
        "_routing": "acme",
        "_source": {
          "original_uri": "gs://bubket/costarica-moths/images/00-SRNP-10366-DHJ96014.jpg",
          "id": None,
          "annotations": None,
          "job_id": "AVvaFoMsrwRXigckTEVd"
        }
      }
    ]
  }
}


class ImageDataTests(unittest.TestCase):
    def test_elasticsearch_role(self):
        image = ImageData.from_elasticsearch(ES_JSON_RESPONSE['hits']['hits'][0])
        representation = image.to_primitive(role='elasticsearch')
        self.assertFalse('id' in representation)
        self.assertFalse('version' in representation)



if __name__ == '__main__':
    import unittest

    unittest.main()
