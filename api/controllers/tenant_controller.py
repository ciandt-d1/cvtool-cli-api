import connexion
from swagger_server.models.tenant import Tenant
from swagger_server.models.tenants import Tenants
from datetime import date, datetime
from typing import List, Dict
from six import iteritems
from ..util import deserialize_date, deserialize_datetime


def get_tenant(tenant_id):
    """
    get_tenant
    get a specific tenant
    :param tenant_id: tenant id
    :type tenant_id: str

    :rtype: Tenant
    """
    return 'do some magic!'


def get_tenants():
    """
    get_tenants
    List all tenants

    :rtype: Tenants
    """
    return 'do some magic!'


def post_tenant(tenant):
    """
    post_tenant
    Creates a new tenant
    :param tenant: Tenant to create
    :type tenant: dict | bytes

    :rtype: Tenant
    """
    if connexion.request.is_json:
        tenant = Tenant.from_dict(connexion.request.get_json())
    return 'do some magic!'


def put_tenant(tenant_id, tenant):
    """
    put_tenant
    updates a tenant
    :param tenant_id: tenant id
    :type tenant_id: str
    :param tenant: Tenant to update
    :type tenant: dict | bytes

    :rtype: Tenant
    """
    if connexion.request.is_json:
        tenant = Tenant.from_dict(connexion.request.get_json())
    return 'do some magic!'
