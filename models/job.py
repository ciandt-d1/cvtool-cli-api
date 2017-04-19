# coding: utf-8

from __future__ import absolute_import
from kingpick.models.job_input_parameters import JobInputParameters
from .base_model_ import Model
from datetime import date, datetime
from typing import List, Dict
from ..util import deserialize_model


class Job(Model):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, job_id=None, version=None, type=None, status=None, exit_status=None, exit_message=None, create_time=None, start_time=None, end_time=None, last_updated=None, created_by=None, parameters=None):
        """
        Job - a model defined in Swagger

        :param job_id: The job_id of this Job.
        :type job_id: str
        :param version: The version of this Job.
        :type version: str
        :param type: The type of this Job.
        :type type: str
        :param status: The status of this Job.
        :type status: str
        :param exit_status: The exit_status of this Job.
        :type exit_status: str
        :param exit_message: The exit_message of this Job.
        :type exit_message: str
        :param create_time: The create_time of this Job.
        :type create_time: datetime
        :param start_time: The start_time of this Job.
        :type start_time: datetime
        :param end_time: The end_time of this Job.
        :type end_time: datetime
        :param last_updated: The last_updated of this Job.
        :type last_updated: datetime
        :param created_by: The created_by of this Job.
        :type created_by: str
        :param parameters: The parameters of this Job.
        :type parameters: JobInputParameters
        """
        self.swagger_types = {
            'job_id': str,
            'version': str,
            'type': str,
            'status': str,
            'exit_status': str,
            'exit_message': str,
            'create_time': datetime,
            'start_time': datetime,
            'end_time': datetime,
            'last_updated': datetime,
            'created_by': str,
            'parameters': JobInputParameters
        }

        self.attribute_map = {
            'job_id': 'job_id',
            'version': 'version',
            'type': 'type',
            'status': 'status',
            'exit_status': 'exit_status',
            'exit_message': 'exit_message',
            'create_time': 'create_time',
            'start_time': 'start_time',
            'end_time': 'end_time',
            'last_updated': 'last_updated',
            'created_by': 'created_by',
            'parameters': 'parameters'
        }

        self._job_id = job_id
        self._version = version
        self._type = type
        self._status = status
        self._exit_status = exit_status
        self._exit_message = exit_message
        self._create_time = create_time
        self._start_time = start_time
        self._end_time = end_time
        self._last_updated = last_updated
        self._created_by = created_by
        self._parameters = parameters

    @classmethod
    def from_dict(cls, dikt):
        """
        Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Job of this Job.
        :rtype: Job
        """
        return deserialize_model(dikt, cls)

    @property
    def job_id(self):
        """
        Gets the job_id of this Job.
        Job id.

        :return: The job_id of this Job.
        :rtype: str
        """
        return self._job_id

    @job_id.setter
    def job_id(self, job_id):
        """
        Sets the job_id of this Job.
        Job id.

        :param job_id: The job_id of this Job.
        :type job_id: str
        """

        self._job_id = job_id

    @property
    def version(self):
        """
        Gets the version of this Job.
        doc version

        :return: The version of this Job.
        :rtype: str
        """
        return self._version

    @version.setter
    def version(self, version):
        """
        Sets the version of this Job.
        doc version

        :param version: The version of this Job.
        :type version: str
        """

        self._version = version

    @property
    def type(self):
        """
        Gets the type of this Job.
        Job type

        :return: The type of this Job.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """
        Sets the type of this Job.
        Job type

        :param type: The type of this Job.
        :type type: str
        """

        self._type = type

    @property
    def status(self):
        """
        Gets the status of this Job.
        Job status

        :return: The status of this Job.
        :rtype: str
        """
        return self._status

    @status.setter
    def status(self, status):
        """
        Sets the status of this Job.
        Job status

        :param status: The status of this Job.
        :type status: str
        """

        self._status = status

    @property
    def exit_status(self):
        """
        Gets the exit_status of this Job.
        Job exit status code

        :return: The exit_status of this Job.
        :rtype: str
        """
        return self._exit_status

    @exit_status.setter
    def exit_status(self, exit_status):
        """
        Sets the exit_status of this Job.
        Job exit status code

        :param exit_status: The exit_status of this Job.
        :type exit_status: str
        """

        self._exit_status = exit_status

    @property
    def exit_message(self):
        """
        Gets the exit_message of this Job.
        Job exit status message

        :return: The exit_message of this Job.
        :rtype: str
        """
        return self._exit_message

    @exit_message.setter
    def exit_message(self, exit_message):
        """
        Sets the exit_message of this Job.
        Job exit status message

        :param exit_message: The exit_message of this Job.
        :type exit_message: str
        """

        self._exit_message = exit_message

    @property
    def create_time(self):
        """
        Gets the create_time of this Job.
        Job creation time

        :return: The create_time of this Job.
        :rtype: datetime
        """
        return self._create_time

    @create_time.setter
    def create_time(self, create_time):
        """
        Sets the create_time of this Job.
        Job creation time

        :param create_time: The create_time of this Job.
        :type create_time: datetime
        """

        self._create_time = create_time

    @property
    def start_time(self):
        """
        Gets the start_time of this Job.
        Job start time

        :return: The start_time of this Job.
        :rtype: datetime
        """
        return self._start_time

    @start_time.setter
    def start_time(self, start_time):
        """
        Sets the start_time of this Job.
        Job start time

        :param start_time: The start_time of this Job.
        :type start_time: datetime
        """

        self._start_time = start_time

    @property
    def end_time(self):
        """
        Gets the end_time of this Job.
        Job end time

        :return: The end_time of this Job.
        :rtype: datetime
        """
        return self._end_time

    @end_time.setter
    def end_time(self, end_time):
        """
        Sets the end_time of this Job.
        Job end time

        :param end_time: The end_time of this Job.
        :type end_time: datetime
        """

        self._end_time = end_time

    @property
    def last_updated(self):
        """
        Gets the last_updated of this Job.
        Job last update

        :return: The last_updated of this Job.
        :rtype: datetime
        """
        return self._last_updated

    @last_updated.setter
    def last_updated(self, last_updated):
        """
        Sets the last_updated of this Job.
        Job last update

        :param last_updated: The last_updated of this Job.
        :type last_updated: datetime
        """

        self._last_updated = last_updated

    @property
    def created_by(self):
        """
        Gets the created_by of this Job.
        Job creator

        :return: The created_by of this Job.
        :rtype: str
        """
        return self._created_by

    @created_by.setter
    def created_by(self, created_by):
        """
        Sets the created_by of this Job.
        Job creator

        :param created_by: The created_by of this Job.
        :type created_by: str
        """

        self._created_by = created_by

    @property
    def parameters(self):
        """
        Gets the parameters of this Job.

        :return: The parameters of this Job.
        :rtype: JobInputParameters
        """
        return self._parameters

    @parameters.setter
    def parameters(self, parameters):
        """
        Sets the parameters of this Job.

        :param parameters: The parameters of this Job.
        :type parameters: JobInputParameters
        """

        self._parameters = parameters

