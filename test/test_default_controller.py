# coding: utf-8

from __future__ import absolute_import

from . import BaseTestCase
from six import BytesIO
from flask import json


class TestDefaultController(BaseTestCase):
    """ DefaultController integration test stubs """

    def test_setup(self):
        """
        Test case for setup

        
        """
        response = self.client.open('/v1/setup',
                                    method='POST')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
