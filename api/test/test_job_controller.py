# coding: utf-8

from __future__ import absolute_import

from kingpick.models.job import Job
from kingpick.models.job_step import JobStep
from kingpick.models.new_job_request import NewJobRequest
from . import BaseTestCase
from six import BytesIO
from flask import json


class TestJobController(BaseTestCase):
    """ JobController integration test stubs """

    # def test_add_step(self):
    #     """
    #     Test case for add_step

        
    #     """
    #     job_step = JobStep()
    #     query_string = [('tenant_id', 'tenant_id_example')]
    #     response = self.client.open('/v1/jobs/{job_id}/steps'.format(job_id='job_id_example'),
    #                                 method='POST',
    #                                 data=json.dumps(job_step),
    #                                 content_type='application/json',
    #                                 query_string=query_string)
    #     self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_create(self):
        """
        Test case for create

        
        """
        new_job_request = NewJobRequest(type='csv')
        query_string = [('tenant_id', 'tenant_id_example'),
                        ('project_id', 'project_id_example')]
        response = self.client.open('/v1/jobs',
                                    method='POST',
                                    data=json.dumps(new_job_request),
                                    content_type='application/json',
                                    query_string=query_string)
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    # def test_end_job(self):
    #     """
    #     Test case for end_job

        
    #     """
    #     query_string = [('tenant_id', 'tenant_id_example')]
    #     response = self.client.open('/v1/jobs/{job_id}/end'.format(job_id='job_id_example'),
    #                                 method='POST',
    #                                 query_string=query_string)
    #     self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    # def test_get(self):
    #     """
    #     Test case for get

        
    #     """
    #     query_string = [('tenant_id', 'tenant_id_example')]
    #     response = self.client.open('/v1/jobs/{job_id}'.format(job_id='job_id_example'),
    #                                 method='GET',
    #                                 query_string=query_string)
    #     self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    # def test_start_job(self):
    #     """
    #     Test case for start_job

        
    #     """
    #     query_string = [('tenant_id', 'tenant_id_example')]
    #     response = self.client.open('/v1/jobs/{job_id}/start'.format(job_id='job_id_example'),
    #                                 method='POST',
    #                                 query_string=query_string)
    #     self.assert200(response, "Response body is : " + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
