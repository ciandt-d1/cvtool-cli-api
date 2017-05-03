# coding: utf-8

from __future__ import absolute_import

from swagger_server.models.image_request import ImageRequest
from swagger_server.models.image_response import ImageResponse
from . import BaseTestCase
from six import BytesIO
from flask import json


class TestImageController(BaseTestCase):
    """ ImageController integration test stubs """

    def test_add(self):
        """
        Test case for add

        
        """
        image_request = ImageRequest()
        query_string = [('tenant_id', 'tenant_id_example'),
                        ('project_id', 'project_id_example')]
        response = self.client.open('/v1images',
                                    method='POST',
                                    data=json.dumps(image_request),
                                    content_type='application/json',
                                    query_string=query_string)
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
