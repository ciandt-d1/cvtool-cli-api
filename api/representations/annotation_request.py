# coding: utf-8

from __future__ import absolute_import
from api.representations.annotations import Annotations
from .base_model_ import Model
from datetime import date, datetime
from typing import List, Dict
from ..util import deserialize_model


class AnnotationRequest(Model):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, ids=None, annotations=None):
        """
        AnnotationRequest - a model defined in Swagger

        :param ids: The ids of this AnnotationRequest.
        :type ids: List[str]
        :param annotations: The annotations of this AnnotationRequest.
        :type annotations: Annotations
        """
        self.swagger_types = {
            'ids': List[str],
            'annotations': Annotations
        }

        self.attribute_map = {
            'ids': 'ids',
            'annotations': 'annotations'
        }

        self._ids = ids
        self._annotations = annotations

    @classmethod
    def from_dict(cls, dikt):
        """
        Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The AnnotationRequest of this AnnotationRequest.
        :rtype: AnnotationRequest
        """
        return deserialize_model(dikt, cls)

    @property
    def ids(self):
        """
        Gets the ids of this AnnotationRequest.
        Id of images to annotate.

        :return: The ids of this AnnotationRequest.
        :rtype: List[str]
        """
        return self._ids

    @ids.setter
    def ids(self, ids):
        """
        Sets the ids of this AnnotationRequest.
        Id of images to annotate.

        :param ids: The ids of this AnnotationRequest.
        :type ids: List[str]
        """

        self._ids = ids

    @property
    def annotations(self):
        """
        Gets the annotations of this AnnotationRequest.

        :return: The annotations of this AnnotationRequest.
        :rtype: Annotations
        """
        return self._annotations

    @annotations.setter
    def annotations(self, annotations):
        """
        Sets the annotations of this AnnotationRequest.

        :param annotations: The annotations of this AnnotationRequest.
        :type annotations: Annotations
        """

        self._annotations = annotations

