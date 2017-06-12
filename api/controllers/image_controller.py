import json
import logging
import tempfile
import uuid

import connexion
from google.cloud._helpers import _to_bytes
from google.cloud.bigquery import SchemaField

from api.domain import image_hash
from api.domain.image import ImageRepository, ImageData
from api.infrastructure import vision
from api.infrastructure.elasticsearch import ES, INDEX_NAME
from api.representations import Error, ImageListResponse, ImageResponse, MetaListResponse
from .job_controller import job_repository

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

    if connexion.request.is_json:
        image = ImageData(image_request, strict=False)

        if image_repository.get_by_original_uri(tenant_id, image.original_uri) is None:

            similar_image_uri = image_hash.exists_similar_image(tenant_id, image)

            if not similar_image_uri:
                job = job_repository.get_by_id(tenant_id, image.job_id)
                vision_result = vision.detect(image, job.vision_api_features)
                image.vision_annotations = json.dumps(vision_result.raw_response)
                image_hash.add(tenant_id, image)
            else:
                logger.info('Similar image was already ingested, cloning vision API data')
                image_already_ingested = image_repository.get_by_original_uri(tenant_id, similar_image_uri)
                image.vision_annotations = image_already_ingested.vision_annotations
                image.similar = image_already_ingested.original_uri

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


def export(tenant_id):
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
            ]),

            SchemaField('cropHintsAnnotation', 'RECORD', mode='REPEATED', fields=[
                SchemaField('importanceFraction', 'FLOAT', mode='NULLABLE'),
                SchemaField('confidence', 'FLOAT', mode='NULLABLE'),
                SchemaField('cropHints', 'RECORD', mode='REPEATED', fields=[
                    SchemaField('boundingPoly', 'RECORD', mode='REPEATED', fields=[
                        SchemaField('x', 'INTEGER', mode='NULLABLE'),
                        SchemaField('y', 'INTEGER', mode='NULLABLE')
                    ])
                ])
            ]),

            SchemaField('textAnnotations', 'RECORD', mode='REPEATED', fields=[
                SchemaField('description', 'STRING', mode='NULLABLE'),
                SchemaField('locale', 'STRING', mode='NULLABLE'),
                SchemaField('boundingPoly', 'RECORD', mode='REPEATED', fields=[
                    SchemaField('x', 'INTEGER', mode='NULLABLE'),
                    SchemaField('y', 'INTEGER', mode='NULLABLE')
                ])
            ])

        ])
    ]

    offset = 0
    limit = 100
    file_name = str(uuid.uuid4())
    bucket_name = 'cvtool-working-bucket'  # TODO: Remove this from the code

    logger.info('Starting export for tenant: %s', tenant_id)

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob_name = 'image-export/{tenant_id}/{export_id}.json'.format(tenant_id=tenant_id, export_id=file_name)
    blob = storage.Blob(blob_name, bucket)
    total = list_all(tenant_id, offset=0, limit=1).meta.total

    logger.info('%s image(s) to export', total)

    with tempfile.NamedTemporaryFile() as tmp_file:
        while offset < total:
            logger.debug('About to fetch image batch: offset: %s, limit: %s', offset, limit)
            api_response = list_all(tenant_id, offset=offset, limit=limit)
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

    if bq_table.exists():
        bq_table.delete()
    if not bq_table.exists():
        bq_table.create()

    source_uri = 'gs://{}/image-export/{}/{}.json'.format(bucket_name, tenant_id, file_name)

    job = bq_client.load_table_from_storage(str(uuid.uuid4()), bq_table, source_uri)
    job.source_format = 'NEWLINE_DELIMITED_JSON'
    job.write_disposition = 'WRITE_TRUNCATE'

    logger.info('Starting job')
    job.begin()

    # retry_count = 100
    # while retry_count > 0 and job.state != 'DONE':
    #     retry_count -= 1
    #     time.sleep(10)
    #     logger.info('Reloading %s', job)
    #     job.reload()  # API call

    logger.info('%s', job)
    logger.info('%s, %s, %s, %s', job.name, job.job_type, job.created, job.state)

    return 'Ok', 200
