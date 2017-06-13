import connexion
from elasticsearch import TransportError

from api.domain.tenant import TenantData
from api.infrastructure.elasticsearch import ES, INDEX_NAME
from api.representations.tenant import Tenant
from api.representations.tenants import Tenants


def get_tenant(tenant_id):
    """
    get_tenant
    get a specific tenant
    :param tenant_id: tenant id
    :type tenant_id: str

    :rtype: Tenant
    """

    try:
        hit = ES.get_source(index=INDEX_NAME, id=tenant_id, doc_type=TenantData.Meta.doc_type)
        return Tenant.from_dict(hit)
    except TransportError as tp:
        return tp.info, tp.status_code


def get_tenants():
    """
    get_tenants
    List all tenants

    :rtype: Tenants
    """
    hits = ES.search(index=INDEX_NAME, doc_type=TenantData.Meta.doc_type, version=True)
    tenants = list(map(lambda hit: Tenant.from_dict(hit.get('_source')), hits.get('hits', {'hits': []}).get('hits')))
    return Tenants(items=tenants)


def post_tenant(tenant):
    """
    post_tenant
    Creates a new tenant

    https://www.elastic.co/guide/en/elasticsearch/guide/current/faking-it.html

    :param tenant: Tenant to create
    :type tenant: dict | bytes

    :rtype: Tenant
    """
    if connexion.request.is_json:
        tenant_data = TenantData(tenant, strict=False)
        tenant_data.check_required_settings()
        ES.create(index=INDEX_NAME, doc_type=TenantData.Meta.doc_type, id=tenant_data.id, body=tenant_data.to_primitive(role='elasticsearch'))
        alias_name = tenant_data.id
        alias_cfg = {
            "routing": tenant_data.id,
            "filter": {
                "term": {
                    "tenant_id": tenant_data.id
                }
            }
        }
        ES.indices.put_alias(index=INDEX_NAME, name=alias_name, body=alias_cfg)
        return tenant, 201


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
