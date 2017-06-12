import json
import logging

from google.cloud import vision, storage
from google.cloud.vision.annotations import Annotations, _process_image_annotations
from google.cloud.vision.feature import Feature
from google.protobuf import json_format

logger = logging.getLogger(__name__)


def from_pb(response):
    data = json_format.MessageToJson(response)
    annotations = Annotations(**_process_image_annotations(response))
    annotations._raw_response = data
    return annotations

Annotations.from_pb = from_pb
Annotations.raw_response = property(lambda self: self._raw_response if hasattr(self, '_raw_response') else None)


def detect(image, features, store_raw_gcs=False):

    client = vision.Client()
    logger.debug('About to detect [%s] for image %s', features, image.original_uri)
    vision_image = client.image(source_uri=image.original_uri)
    vision_result_list = vision_image.detect([Feature(feature_type, 100) for feature_type in features])
    vision_result = vision_result_list[0] if vision_result_list and len(vision_result_list) > 0 else None

    if vision_result:
        logger.debug(json.dumps(vision_result.raw_response))

        if store_raw_gcs:
            logger.debug('About save raw json into GCS')
            storage_client = storage.Client()
            bucket_name = image.original_uri
            bucket = storage_client.get_bucket(bucket_name)
            blob_name = image.original_uri + '.json'
            blob = storage.Blob(blob_name, bucket)
            content_type = 'application/json'
            ret_val = blob.upload_from_file(vision_result.raw_response, content_type=content_type, client=storage_client, rewind=True)
            # logger.debug('Temporary file uploaded: %s', ret_val)

    return vision_result
