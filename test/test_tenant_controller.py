# coding: utf-8

from __future__ import absolute_import

from kingpick.models.tenant import Tenant
from kingpick.models.tenants import Tenants
from . import BaseTestCase
from six import BytesIO
from flask import json


class TestTenantController(BaseTestCase):
    """ TenantController integration test stubs """

    def test_get_tenant(self):
        """
        Test case for get_tenant

        
        """
        response = self.client.open('/v1/tenants/{tenant_id}'.format(tenant_id='tenant_id_example'),
                                    method='GET')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_get_tenants(self):
        """
        Test case for get_tenants

        
        """
        response = self.client.open('/v1/tenants',
                                    method='GET')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_post_tenant(self):
        """
        Test case for post_tenant

        
        """
        tenant = Tenant()
        response = self.client.open('/v1/tenants',
                                    method='POST',
                                    data=json.dumps(tenant),
                                    content_type='application/json')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))

    def test_put_tenant(self):
        """
        Test case for put_tenant

        
        """
        tenant = Tenant()
        response = self.client.open('/v1/tenants/{tenant_id}'.format(tenant_id='tenant_id_example'),
                                    method='PUT',
                                    data=json.dumps(tenant),
                                    content_type='application/json')
        self.assert200(response, "Response body is : " + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
