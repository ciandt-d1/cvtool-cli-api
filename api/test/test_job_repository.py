# coding: utf-8

from __future__ import absolute_import

import logging
import unittest

from elasticsearch import Elasticsearch, TransportError

from ..domain.job import JobData, JobRepository

ES = Elasticsearch('http://localhost:9200')

logger = logging.getLogger(__name__)


class TestJobRepository(unittest.TestCase):

    def test_save(self):
        repository = JobRepository(ES)
        job = JobData()
        job.tenant_id = 'acme'
        print(repository.save(job).to_native())

    # def test_save2(self):
    #     job = JobData.get_mock_object()
    #     job.id = '1431242'
    #     job.tenant_id = 'acme'
    #     print(job.flatten(role='public'))

if __name__ == '__main__':
    import unittest
    unittest.main()
