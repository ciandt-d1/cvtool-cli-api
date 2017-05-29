import json
import logging
import os
import tempfile
import uuid

import connexion
import cvtool_image_hashes_client
import time
from google.cloud import vision, storage, bigquery
from google.cloud._helpers import _to_bytes
from google.cloud.bigquery import SchemaField
from google.cloud.vision.feature import Feature, FeatureTypes

from api.domain.image import ImageRepository, ImageData
from api.infrastructure.elasticsearch import ES, INDEX_NAME
from api.representations import Error, ImageListResponse, ImageResponse, MetaListResponse
from images import count, get

logger = logging.getLogger(__name__)
image_repository = ImageRepository(ES, INDEX_NAME)


def add(tenant_id, image_request):
    """
    add
    Adds an image to the database.
    :param tenant_id: tenant id
    :type tenant_id: str
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
                vertices.append({'x': vertice.x_coordinate, 'y': vertice.y_coordinate})
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
                vertices.append({'x': vertice.x_coordinate, 'y': vertice.y_coordinate})
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
                vertices.append({'x': vertice.x_coordinate, 'y': vertice.y_coordinate})
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
        if image_repository.get_by_original_uri(tenant_id, image.original_uri) is None:

            # Check if an image with similar phash was already added
            cvtool_image_hashes_client.configuration.host = os.environ['IMAGE_HASHES_API_HOST']
            cvtool_image_hashes_client.configuration.debug = os.environ.get('DEBUG', None) is not None
            image_hashes_api_instance = cvtool_image_hashes_client.DefaultApi()
            image_hash_search_request = cvtool_image_hashes_client.ImageHashSearchRequest(url=image.original_uri)

            try:
                image_hashes_api_response = image_hashes_api_instance.search(tenant_id, 'default_project',
                                                                             image_hash_search_request)
                logger.debug(image_hashes_api_response)
                if len(image_hashes_api_response.results) == 0:
                    # Getting vision api information from Google
                    client = vision.Client()
                    vision_image = client.image(source_uri=image.original_uri)
                    features = [Feature(FeatureTypes.LABEL_DETECTION, 100),  # TODO: Get FEATURES from job parameter
                                Feature(FeatureTypes.LANDMARK_DETECTION, 100),
                                Feature(FeatureTypes.LOGO_DETECTION, 100),
                                Feature(FeatureTypes.IMAGE_PROPERTIES, 100),
                                Feature(FeatureTypes.SAFE_SEARCH_DETECTION, 100)]
                    vision_result = vision_image.detect(features)
                    image.vision_annotations = json.dumps(vision_model(vision_result[0]))

                    # Adding image to hashes database
                    image_hash_request = cvtool_image_hashes_client.ImageHashRequest(url=image.original_uri)
                    insert_image_hashes_api_response = image_hashes_api_instance.add(tenant_id, 'default_project',
                                                                                     image_hash_request)
                    logger.debug(insert_image_hashes_api_response)
                else:
                    # Clonning vision api information from another image
                    logger.info('Similar image was already ingested, cloning vision API data')
                    image_already_ingested = image_repository.get_by_original_uri(
                        tenant_id, image_hashes_api_response.results[0].filepath)
                    image.vision_annotations = image_already_ingested.vision_annotations
                    image.similar = image_already_ingested.original_uri

            except Exception:
                logger.exception('Error')

            # Adding image to repository
            image = image_repository.save(tenant_id, image)
            logger.info('New image ingested: ' + str(image.flatten()))

            return ImageResponse.from_dict(image.flatten())
        else:
            return Error(code=400, message='Duplicate images are not allowed'), 400


def list_all(tenant_id, offset=None, limit=None):
    """
    list
    Adds an image to the database.
    :param tenant_id: tenant id
    :type tenant_id: str
    :param offset: offset
    :type offset: int
    :param limit: limit
    :type limit: int

    :rtype: ImageListResponse
    """

    total, all_images = image_repository.get_all(tenant_id, offset, limit)

    # FIXME must be simplified - too much dict<->object transformations
    return ImageListResponse(
        items=[ImageResponse.from_dict(img.to_primitive()) for img in all_images],
        meta=MetaListResponse(offset=offset, limit=limit, total=total)
    )


def export(tenant_id, bucket_name):
    SCHEMA = [
        SchemaField('project_id', 'STRING', mode='NULLABLE'),
        SchemaField('id', 'STRING', mode='REQUIRED'),
        SchemaField('version', 'STRING', mode='REQUIRED'),
        SchemaField('job_id', 'STRING', mode='REQUIRED'),
        SchemaField('original_uri', 'STRING', mode='NULLABLE'),
        SchemaField('exif_annotations', 'RECORD', mode='REPEATED', fields=[
            SchemaField('key', 'STRING', mode='REQUIRED'),
            SchemaField('value', 'STRING', mode='REQUIRED')
        ]),

        SchemaField('vision_annotations', 'RECORD', mode='NULLABLE', fields=[
            SchemaField('safeSearchAnnotation', 'RECORD', mode='NULLABLE', fields=[
                SchemaField('adult', 'STRING', mode='NULLABLE'),
                SchemaField('spoof', 'STRING', mode='NULLABLE'),
                SchemaField('medical', 'STRING', mode='NULLABLE'),
                SchemaField('violence', 'STRING', mode='NULLABLE')
            ]),
            SchemaField('labelAnnotations', 'RECORD', mode='REPEATED', fields=[
                SchemaField('mid', 'STRING', mode='NULLABLE'),
                SchemaField('locale', 'STRING', mode='NULLABLE'),
                SchemaField('description', 'STRING', mode='NULLABLE'),
                SchemaField('score', 'FLOAT', mode='NULLABLE'),
                SchemaField('boundingPoly', 'RECORD', mode='REPEATED', fields=[
                    SchemaField('x', 'INTEGER', mode='NULLABLE'),
                    SchemaField('y', 'INTEGER', mode='NULLABLE')
                ])
            ]),
            SchemaField('landmarkAnnotations', 'RECORD', mode='REPEATED', fields=[
                SchemaField('mid', 'STRING', mode='NULLABLE'),
                SchemaField('locale', 'STRING', mode='NULLABLE'),
                SchemaField('description', 'STRING', mode='NULLABLE'),
                SchemaField('score', 'FLOAT', mode='NULLABLE'),
                SchemaField('boundingPoly', 'RECORD', mode='REPEATED', fields=[
                    SchemaField('x', 'INTEGER', mode='NULLABLE'),
                    SchemaField('y', 'INTEGER', mode='NULLABLE')
                ])
            ]),
            SchemaField('logoAnnotations', 'RECORD', mode='REPEATED', fields=[
                SchemaField('mid', 'STRING', mode='NULLABLE'),
                SchemaField('locale', 'STRING', mode='NULLABLE'),
                SchemaField('description', 'STRING', mode='NULLABLE'),
                SchemaField('score', 'FLOAT', mode='NULLABLE'),
                SchemaField('boundingPoly', 'RECORD', mode='REPEATED', fields=[
                    SchemaField('x', 'INTEGER', mode='NULLABLE'),
                    SchemaField('y', 'INTEGER', mode='NULLABLE')
                ])
            ]),
            SchemaField('imagePropertiesAnnotation', 'RECORD', mode='NULLABLE', fields=[
                SchemaField('dominantColors', 'RECORD', mode='NULLABLE', fields=[
                    SchemaField('colors', 'RECORD', mode='REPEATED', fields=[
                        SchemaField('pixelFraction', 'FLOAT', mode='NULLABLE'),
                        SchemaField('score', 'FLOAT', mode='NULLABLE'),
                        SchemaField('color', 'RECORD', mode='NULLABLE', fields=[
                            SchemaField('red', 'FLOAT', mode='NULLABLE'),
                            SchemaField('green', 'FLOAT', mode='NULLABLE'),
                            SchemaField('blue', 'FLOAT', mode='NULLABLE'),
                            SchemaField('alpha', 'FLOAT', mode='NULLABLE')
                        ]),
                    ])
                ])
            ])
        ])
    ]

    offset = 0
    limit = 100
    project_id = 'default_project'
    file_name = str(uuid.uuid4())

    logger.info('Starting export for tenant: %s', tenant_id)

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob_name = 'image-export/{tenant_id}/{export_id}.json'.format(tenant_id=tenant_id, export_id=file_name)
    blob = storage.Blob(blob_name, bucket)
    total = count(tenant_id, project_id)

    logger.info('%s image(s) to export', total)

    with tempfile.NamedTemporaryFile() as tmp_file:
        while offset < total:
            logger.debug('About to fetch image batch: offset: %s, limit: %s', offset, limit)
            api_response = get(tenant_id, project_id, offset=offset, limit=limit)
            items = api_response.items
            logger.debug('Got batch with %s image(s)', len(items))
            for image in items:
                logger.debug('Writing image: %s', image.id)

                image_to_dict = image.to_dict()

                del image_to_dict['annotations']

                exif_annotations_dict = image_to_dict.pop('exif_annotations', {})
                if exif_annotations_dict:
                    image_to_dict['exif_annotations'] = [dict(key=k, value=v) for k, v in exif_annotations_dict.items()]

                vision_annotations_dict = image_to_dict.pop('vision_annotations', {})
                if vision_annotations_dict:
                    image_to_dict['vision_annotations'] = json.loads(vision_annotations_dict)

                tmp_file.write(_to_bytes(json.dumps(image_to_dict) + '\n', encoding='utf-8'))
            offset += limit

        content_type = 'application/json'
        ret_val = blob.upload_from_file(tmp_file, content_type=content_type, client=storage_client, rewind=True)
        logger.debug('Temporary file uploaded: %s', ret_val)

    logger.info('Images exported and stored on: %s', blob.path)

    bq_client = bigquery.Client()

    dataset = bq_client.dataset(tenant_id)
    if not dataset.exists():
        dataset.create()

    bq_table = dataset.table('images', SCHEMA)
    # TODO add flag to force table recreation
    # if bq_table.exists():
    #     bq_table.delete()
    if not bq_table.exists():
        bq_table.create()

    source_uri = 'gs://{}/image-export/{}/{}.json'.format(bucket_name, tenant_id, file_name)

    job = bq_client.load_table_from_storage(str(uuid.uuid4()), bq_table, source_uri)
    job.source_format = 'NEWLINE_DELIMITED_JSON'
    job.write_disposition = 'WRITE_TRUNCATE'

    logger.info('Starting job')
    job.begin()

    retry_count = 100
    while retry_count > 0 and job.state != 'DONE':
        retry_count -= 1
        time.sleep(10)
        logger.info('Reloading %s', job)
        job.reload()  # API call

    logger.info('%s', job)
    logger.info('%s, %s, %s, %s', job.name, job.job_type, job.created, job.state)

