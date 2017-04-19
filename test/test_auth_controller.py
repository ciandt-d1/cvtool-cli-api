# coding: utf-8

from __future__ import absolute_import

from . import BaseTestCase
from six import BytesIO
from flask import json


class TestAuthController(BaseTestCase):
    """ AuthController integration test stubs """

    def test_token(self):
        """
        Test case for token

        
        """
        response = self.client.open('/v1/auth/token',
                                    method='GET')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
