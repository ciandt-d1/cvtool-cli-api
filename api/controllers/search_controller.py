import connexion
import logging

from api.domain.image import ImageRepository
from api.infrastructure.elasticsearch import ES, INDEX_NAME
from api.representations import ImageListResponse, ImageResponse, MetaListResponse
from api.representations.image_list_response import ImageListResponse
from api.representations.image_search_request import ImageSearchRequest

logger = logging.getLogger(__name__)
image_repository = ImageRepository(ES, INDEX_NAME)


def search_images(tenant_id, offset=0, limit=100):
    """
    search_images
    Search for images.
    :param tenant_id: tenant id
    :type tenant_id: str
    :param offset: offset
    :type offset: int
    :param limit: limit
    :type limit: int

    :rtype: ImageListResponse
    """
    if connexion.request.is_json:
        request = ImageSearchRequest.from_dict(connexion.request.get_json())
        if request.custom_query:
            total, all_images = image_repository.search(tenant_id, request.custom_query, offset, limit)
            return ImageListResponse(
                items=[ImageResponse.from_dict(img.to_primitive()) for img in all_images],
                meta=MetaListResponse(offset=offset, limit=limit, total=total)
            )
