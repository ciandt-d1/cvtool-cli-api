import connexion
from datetime import date, datetime
from typing import List, Dict
from six import iteritems
from ..util import deserialize_date, deserialize_datetime


def token():
    """
    token
    Generate a new authentication token

    :rtype: str
    """
    return 'do some magic!'
