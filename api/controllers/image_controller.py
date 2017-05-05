import logging

import connexion

from api.domain.image import ImageRepository, ImageData
from api.representations.image_response import ImageResponse
from api.infrastructure.elasticsearch import ES, INDEX_NAME

logger = logging.getLogger(__name__)
image_repository = ImageRepository(ES, INDEX_NAME)


def add(tenant_id, project_id, image_request):
    """
    add
    Adds an image signature to the database.
    :param tenant_id: tenant id
    :type tenant_id: str
    :param project_id: project id
    :type project_id: str
    :param image_request: Image to create
    :type image_request: dict | bytes

    :rtype: ImageResponse
    """

    if connexion.request.is_json:
        image = ImageData(image_request, strict=False)

        if image_repository.get_by_original_uri(tenant_id, image.original_uri) is None:
            image = image_repository.save(tenant_id, project_id, image)
        else:
            return None

    return ImageResponse.from_dict(image.flatten())
