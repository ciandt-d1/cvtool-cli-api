import connexion
from elasticsearch import Elasticsearch, TransportError
from api.models.tenants import Tenants

from api.models.tenant import Tenant

ES = Elasticsearch('http://elasticsearch:9200')
INDEX_NAME = 'kingpick'
TENANT_DOC_TYPE = 'tenant'

def get_tenant(tenant_id):
    """
    get_tenant
    get a specific tenant
    :param tenant_id: tenant id
    :type tenant_id: str

    :rtype: Tenant
    """

    try:
        hit = ES.get_source(index=INDEX_NAME, id=tenant_id, doc_type=TENANT_DOC_TYPE)
        return Tenant.from_dict(hit)
    except TransportError as tp:
        return tp.info, tp.status_code


def get_tenants():
    """
    get_tenants
    List all tenants

    :rtype: Tenants
    """
    hits = ES.search(index=INDEX_NAME, doc_type=TENANT_DOC_TYPE, version=True)
    tenants = list(map(lambda hit: Tenant.from_dict(hit.get('_source')), hits.get('hits', { 'hits': [] }).get('hits')))
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
        tenant = Tenant.from_dict(connexion.request.get_json())
        ES.create(index=INDEX_NAME, doc_type=TENANT_DOC_TYPE, id=tenant.id, body=tenant.to_dict())
        alias_name = tenant.id
        alias_cfg = {
            "routing": tenant.id,
            "filter": {
                "term": {
                    "tenant_id": tenant.id
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
