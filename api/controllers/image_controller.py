import json
import logging
import tempfile
import uuid

import connexion
from google.cloud import storage
from google.cloud._helpers import _to_bytes

from api.domain import image_hash, tenant as tenant_repository
from api.domain.image import ImageRepository, ImageData
from api.infrastructure import vision, bigquery
from api.infrastructure.elasticsearch import ES, INDEX_NAME
from api.representations import AnnotationRequest, Error, ImageListResponse, ImageResponse, MetaListResponse
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
                if image_request.run_vision_api:
                    vision_result = vision.detect(image, job.vision_api_features)
                    image.vision_annotations = json.dumps(vision_result.raw_response)
                image_hash.add(tenant_id, image)
            else:
                if image_request.run_vision_api:
                    logger.info('Similar image was already ingested, cloning vision API data')
                    image_already_ingested = image_repository.get_by_original_uri(tenant_id, similar_image_uri)
                    if image_request.run_vision_api:
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
    tenant = tenant_repository.get_by_id(tenant_id)

    offset = 0
    limit = 100
    file_name = str(uuid.uuid4())
    bucket_name = tenant.staging_bucket

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

    source_uri = 'gs://{}/{}'.format(bucket_name, blob_name)
    job = bigquery.load_table_from_json(tenant, source_uri)

    return 'Ok', 202


def annotate(tenant_id, annotation_request):
    """
    annotate
    Add or change annotations to one or more images.
    :param tenant_id: tenant id
    :type tenant_id: str
    :param annotation_request: Annotations to be associated with image(s)
    :type annotation_request: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        annotation_request = AnnotationRequest.from_dict(connexion.request.get_json())
    return 'do some magic!'
