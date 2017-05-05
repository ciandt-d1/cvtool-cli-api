from api.infrastructure.elasticsearch import ES, INDEX_NAME, INDEX_BODY


def setup():
    """
    setup
    Setup basic infrastructure

    :rtype: None
    """
    ES.indices.delete_alias(index='*', name='_all', ignore=[404])
    ES.indices.delete(index='*', ignore=[404])
    ES.indices.create(index=INDEX_NAME, body=INDEX_BODY, update_all_types=True)
    return 'Up and running!'

