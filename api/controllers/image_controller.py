import json
import logging

import connexion
from google.cloud import vision
from google.cloud.vision.feature import Feature, FeatureTypes

from api.domain.image import ImageRepository, ImageData
from api.infrastructure.elasticsearch import ES, INDEX_NAME
from api.representations import Error
from api.representations.image_response import ImageResponse

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
        def default(self, obj):
            if hasattr(obj, '__dict__'):
                return obj.__dict__
            return None
            return json.JSONEncoder.default(self, obj)

    if connexion.request.is_json:
        image = ImageData(image_request, strict=False)
        if image_repository.get_by_original_uri(tenant_id, image.original_uri) is None:

            try:
                # TODO: Check phash to avoid Vision API call for the same image
                client = vision.Client()
                vision_image = client.image(source_uri=image.original_uri)

                # TODO: Get FEATURES from job parameter
                features = [Feature(FeatureTypes.LABEL_DETECTION, 10),
                            Feature(FeatureTypes.LANDMARK_DETECTION, 10),
                            Feature(FeatureTypes.LOGO_DETECTION, 10),
                            Feature(FeatureTypes.IMAGE_PROPERTIES, 10),
                            Feature(FeatureTypes.SAFE_SEARCH_DETECTION, 10)]
                vision_result = vision_image.detect(features)
                vision_json = json.dumps(vision_result, cls=VisionResponseEncoder)

                image.vision_raw = vision_json

            except:
                pass

            image = image_repository.save(tenant_id, project_id, image)
            return ImageResponse.from_dict(image.flatten())
        else:
            return Error(code=400, message='Duplicate images are not allowed'), 400
