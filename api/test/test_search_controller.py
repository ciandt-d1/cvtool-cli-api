# coding: utf-8

from __future__ import absolute_import

from api.representations.error import Error
from api.representations.image_list_response import ImageListResponse
from api.representations.image_search_request import ImageSearchRequest
from . import BaseTestCase
from six import BytesIO
from flask import json


class TestSearchController(BaseTestCase):
    """ SearchController integration test stubs """

    def test_search_images(self):
        """
        Test case for search_images

        
        """
        query = ImageSearchRequest()
        query_string = [('tenant_id', 'tenant_id_example'),
                        ('offset', 1),
                        ('limit', 100)]
        response = self.client.open('/v1/search/images',
                                    method='POST',
                                    data=json.dumps(query),
                                    content_type='application/json',
                                    query_string=query_string)
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
