import logging

from ..config import DEBUG, IMAGE_HASHES_API_HOST
import cvtool_image_hashes_client as client

logger = logging.getLogger(__name__)

client.configuration.host = IMAGE_HASHES_API_HOST + '/v1'
client.configuration.debug = DEBUG

image_hashes_api_instance = client.DefaultApi()


def exists_similar_image(tenant_id, image):
    logger.debug('Looking for similar images')
    image_hash_search_request = client.ImageHashSearchRequest(url=image.original_uri)
    image_hashes_api_response = image_hashes_api_instance.search(tenant_id, 'default_project', image_hash_search_request)

    logger.debug(image_hashes_api_response)

    if len(image_hashes_api_response.results) > 0:
        logger.debug('Found %s similar image(s)', len(image_hashes_api_response.results))
        similar_image_uri = image_hashes_api_response.results[0].filepath
        return similar_image_uri
    else:
        return None


def add(tenant_id, image):
    # Adding image to hashes database
    image_hash_request = client.ImageHashRequest(url=image.original_uri, filepath=image.original_uri, metadata=dict(
        image_job_id=image.job_id
    ))
    insert_image_hashes_api_response = image_hashes_api_instance.add(tenant_id, 'default_project', image_hash_request)
    logger.debug(insert_image_hashes_api_response)
