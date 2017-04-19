# coding: utf-8

from __future__ import absolute_import

from models.project import Project
from models.projects import Projects
from . import BaseTestCase
from six import BytesIO
from flask import json


class TestProjectController(BaseTestCase):
    """ ProjectController integration test stubs """

    def test_create_project(self):
        """
        Test case for create_project

        Creates a new project
        """
        project = Project()
        query_string = [('tenant_id', 'tenant_id_example')]
        response = self.client.open('/v1/projects',
                                    method='POST',
                                    data=json.dumps(project),
                                    content_type='application/json',
                                    query_string=query_string)
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_get_project(self):
        """
        Test case for get_project

        
        """
        query_string = [('tenant_id', 'tenant_id_example')]
        response = self.client.open('/v1/projects/{project_id}'.format(project_id='project_id_example'),
                                    method='GET',
                                    query_string=query_string)
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_list_projects(self):
        """
        Test case for list_projects

        
        """
        query_string = [('tenant_id', 'tenant_id_example')]
        response = self.client.open('/v1/projects',
                                    method='GET',
                                    query_string=query_string)
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_put_project(self):
        """
        Test case for put_project

        
        """
        project = Project()
        query_string = [('tenant_id', 'tenant_id_example')]
        response = self.client.open('/v1/projects/{project_id}'.format(project_id='project_id_example'),
                                    method='PUT',
                                    data=json.dumps(project),
                                    content_type='application/json',
                                    query_string=query_string)
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
