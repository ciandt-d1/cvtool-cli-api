import json
import logging

import connexion
import cvtool_image_hashes_client
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

    def vision_model(vision_raw):
        result = {}

        # Safe search
        safe_search_annotation = {'adult': vision_raw.safe_searches.adult.value,
                                  'spoof': vision_raw.safe_searches.spoof.value,
                                  'medical': vision_raw.safe_searches.medical.value,
                                  'violence': vision_raw.safe_searches.violence.value}
        result['safeSearchAnnotation'] = safe_search_annotation

        # Label
        label_annotations = []
        for label in vision_raw.labels:
            vertices = []
            for vertice in label.bounds.vertices:
                vertices.append({'x': vertice.x, 'y': vertice.y})
            label_annotations.append({
                'mid': label.mid,
                'locale': label.locale,
                'description': label.description,
                'score': label.score,
                'boundingPoly': vertices
            })
        result['labelAnnotations'] = label_annotations

        # Landmark
        landmark_annotations = []
        for landmark in vision_raw.landmarks:
            vertices = []
            for vertice in landmark.bounds.vertices:
                vertices.append({'x': vertice.x, 'y': vertice.y})
            landmark_annotations.append({
                'mid': landmark.mid,
                'locale': landmark.locale,
                'description': landmark.description,
                'score': landmark.score,
                'boundingPoly': vertices
            })
        result['landmarkAnnotations'] = landmark_annotations

        # Logo
        logo_annotations = []
        for logo in vision_raw.logos:
            vertices = []
            for vertice in logo.bounds.vertices:
                vertices.append({'x': vertice.x, 'y': vertice.y})
            logo_annotations.append({
                'mid': logo.mid,
                'locale': logo.locale,
                'description': logo.description,
                'score': logo.score,
                'boundingPoly': vertices
            })
        result['logoAnnotations'] = logo_annotations

        # Image Properties
        colors = []
        for color in vision_raw.properties.colors:
            colors.append({
                'color': {'red': color.color.red, 'green': color.color.green, 'blue': color.color.blue,
                          'alpha': color.color.alpha},
                'pixelFraction': color.pixel_fraction,
                'score': color.score
            })
        result['imagePropertiesAnnotation'] = {
            'dominantColors': {
                'colors': colors
            }
        }

        return result

    if connexion.request.is_json:
        image = ImageData(image_request, strict=False)
        if image_repository.get_by_original_uri(tenant_id, project_id, image.original_uri) is None:

            # Check if an image with similar phash was already added
            cvtool_image_hashes_client.configuration.host = os.environ['IMAGE_HASHES_API_HOST']
            cvtool_image_hashes_client.configuration.debug = os.environ.get('DEBUG', None) is not None
            image_hashes_api_instance = cvtool_image_hashes_client.DefaultApi()
            image_hash_search_request = cvtool_image_hashes_client.ImageHashSearchRequest(url=image.original_uri)

            try:
                image_hashes_api_response = image_hashes_api_instance.search(tenant_id, project_id,image_hash_search_request)
                logger.debug(image_hashes_api_response)
                if len(image_hashes_api_response.results) == 0:
                    # Getting vision api information from Google
                    client = vision.Client()
                    vision_image = client.image(source_uri=image.original_uri)
                    features = [Feature(FeatureTypes.LABEL_DETECTION, 100), # TODO: Get FEATURES from job parameter
                                Feature(FeatureTypes.LANDMARK_DETECTION, 100),
                                Feature(FeatureTypes.LOGO_DETECTION, 100),
                                Feature(FeatureTypes.IMAGE_PROPERTIES, 100),
                                Feature(FeatureTypes.SAFE_SEARCH_DETECTION, 100)]
                    vision_result = vision_image.detect(features)
                    image.vision_annotations = json.dumps(vision_model(vision_result[0]))

                    # Adding image to hashes database
                    image_hash_request = cvtool_image_hashes_client.ImageHashRequest(url=image.original_uri)
                    insert_image_hashes_api_response = image_hashes_api_instance.add(tenant_id, project_id,
                                                                                     image_hash_request)
                    logger.debug(insert_image_hashes_api_response)
                else:
                    # Clonning vision api information from another image
                    logger.info('Similar image was already ingested, cloning vision API data')
                    image_already_ingested = image_repository.get_by_original_uri(tenant_id, project_id,
                                                         image_hashes_api_response.results[0].filepath)
                    image.vision_annotations = image_already_ingested.vision_annotations

            except Exception:
                logger.exception('Error')

            # Adding image to repository
            image = image_repository.save(tenant_id, project_id, image)
            logger.info('New image ingested: ' + image)

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
