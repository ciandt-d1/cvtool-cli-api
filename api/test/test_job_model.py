# coding: utf-8

from __future__ import absolute_import

import logging
import unittest

from api.domain.job import JobData

logger = logging.getLogger(__name__)

ES_JSON_RESPONSE = {
   "_index": "acme",
   "_type": "job",
   "_id": "AVvU3uO--Ao87pGaSvmt",
   "_version": 1,
   "found": True,
   "_source": {
      "tenant_id": None,
      "exit_message": None,
      "status": "CREATED",
      "created_by": None,
      "exit_status": None,
      "create_time": "2017-05-04T19:10:26.229124",
      "project_id": None,
      "last_updated": "2017-05-04T19:10:26.239667",
      "input_params": None,
      "version": None,
      "end_time": None,
      "start_time": None,
      "id": None,
      "job_type": "csv"
   }
}



class JobDataTests(unittest.TestCase):
    def test_load_from_es_payload(self):
        job = JobData.from_elasticsearch(ES_JSON_RESPONSE)
        print(job.to_primitive())

if __name__ == '__main__':
    import unittest

    unittest.main()
