# coding: utf-8

from __future__ import absolute_import
from kingpick.models.settings import Settings
from .base_model_ import Model
from datetime import date, datetime
from typing import List, Dict
from ..util import deserialize_model


class Project(Model):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, id: str=None, name: str=None, description: str=None, settings: Settings=None):
        """
        Project - a model defined in Swagger

        :param id: The id of this Project.
        :type id: str
        :param name: The name of this Project.
        :type name: str
        :param description: The description of this Project.
        :type description: str
        :param settings: The settings of this Project.
        :type settings: Settings
        """
        self.swagger_types = {
            'id': str,
            'name': str,
            'description': str,
            'settings': Settings
        }

        self.attribute_map = {
            'id': 'id',
            'name': 'name',
            'description': 'description',
            'settings': 'settings'
        }

        self._id = id
        self._name = name
        self._description = description
        self._settings = settings

    @classmethod
    def from_dict(cls, dikt) -> 'Project':
        """
        Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Project of this Project.
        :rtype: Project
        """
        return deserialize_model(dikt, cls)

    @property
    def id(self) -> str:
        """
        Gets the id of this Project.

        :return: The id of this Project.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id: str):
        """
        Sets the id of this Project.

        :param id: The id of this Project.
        :type id: str
        """

        self._id = id

    @property
    def name(self) -> str:
        """
        Gets the name of this Project.

        :return: The name of this Project.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name: str):
        """
        Sets the name of this Project.

        :param name: The name of this Project.
        :type name: str
        """

        self._name = name

    @property
    def description(self) -> str:
        """
        Gets the description of this Project.

        :return: The description of this Project.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description: str):
        """
        Sets the description of this Project.

        :param description: The description of this Project.
        :type description: str
        """

        self._description = description

    @property
    def settings(self) -> Settings:
        """
        Gets the settings of this Project.

        :return: The settings of this Project.
        :rtype: Settings
        """
        return self._settings

    @settings.setter
    def settings(self, settings: Settings):
        """
        Sets the settings of this Project.

        :param settings: The settings of this Project.
        :type settings: Settings
        """

        self._settings = settings

