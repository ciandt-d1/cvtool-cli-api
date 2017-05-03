import connexion
from swagger_server.models.image_request import ImageRequest
from swagger_server.models.image_response import ImageResponse
from datetime import date, datetime
from typing import List, Dict
from six import iteritems
from ..util import deserialize_date, deserialize_datetime


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
        image_request = ImageRequest.from_dict(connexion.request.get_json())
    return 'do some magic!'
