import json
import logging

import connexion
import cvtool_image_hashes_client
from cvtool_image_hashes_client.rest import ApiException
from google.cloud import vision
from google.cloud.vision.feature import Feature, FeatureTypes

from api.domain.image import ImageRepository, ImageData
from api.infrastructure.elasticsearch import ES, INDEX_NAME
from api.representations import Error, ImageListResponse, ImageResponse, MetaListResponse

logger = logging.getLogger(__name__)
image_repository = ImageRepository(ES, INDEX_NAME)


def add(tenant_id, project_id, image_request):
    """
    add
    Adds an image to the database.
    :param tenant_id: tenant id
    :type tenant_id: str
    :param project_id: project id
    :type project_id: str
    :param image_request: Image to create
    :type image_request: dict | bytes

    :rtype: ImageResponse
    """

    class VisionResponseEncoder(json.JSONEncoder):
        # TODO: better implementation, corresponding to vision api response
        def default(self, obj):
            if hasattr(obj, '__dict__'):
                return obj.__dict__
            return None

    if connexion.request.is_json:
        image = ImageData(image_request, strict=False)
        if image_repository.get_by_original_uri(tenant_id, project_id, image.original_uri) is None:

            # Getting vision api information
            try:
                client = vision.Client()
                vision_image = client.image(source_uri=image.original_uri)

                # TODO: Get FEATURES from job parameter
                features = [Feature(FeatureTypes.LABEL_DETECTION, 100),
                            Feature(FeatureTypes.LANDMARK_DETECTION, 100),
                            Feature(FeatureTypes.LOGO_DETECTION, 100),
                            Feature(FeatureTypes.IMAGE_PROPERTIES, 100),
                            Feature(FeatureTypes.SAFE_SEARCH_DETECTION, 100)]
                vision_result = vision_image.detect(features)
                vision_json = json.dumps(vision_result, cls=VisionResponseEncoder)

                image.vision_raw = vision_json
            except:
                logger.exception('Error using vision api')

            # Adding image to repository
            image = image_repository.save(tenant_id, project_id, image)

            # Adding image to hashes database
            image_hash_request = cvtool_image_hashes_client.ImageHashRequest(url='http://www.offair.org/testPattern.png')
            try:
                api_response = image_hashes_api_instance.add(tenant_id, project_id, image_hash_request)
                logger.debug(api_response)
            except ApiException as e:
                logger.exception("Error when calling DefaultApi->add: %s\n" % e)

            return ImageResponse.from_dict(image.flatten())
        else:
            return Error(code=400, message='Duplicate images are not allowed'), 400


def list_all(tenant_id, project_id, offset=None, limit=None):
    """
    list
    Adds an image to the database.
    :param tenant_id: tenant id
    :type tenant_id: str
    :param project_id: project id
    :type project_id: str
    :param offset: offset
    :type offset: int
    :param limit: limit
    :type limit: int

    :rtype: ImageListResponse
    """


    total, all_images = image_repository.get_all(tenant_id, project_id, offset, limit)

    # FIXME must be simplified - too much dict<->object transformations
    return ImageListResponse(
        items=[ImageResponse.from_dict(img.to_primitive()) for img in all_images],
        meta=MetaListResponse(offset=offset, limit=limit, total=total)
    )
