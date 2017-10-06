import io
import json
import time
from base64 import b64encode
from urllib.parse import urlparse, quote_plus

import datetime
from cryptography.hazmat import backends
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from google.auth import crypt, _helpers

from api.config import URL_SIGNER_SERVICE_ACCOUNT_FILE


_JSON_FILE_PRIVATE_KEY = 'private_key'
_JSON_FILE_PRIVATE_KEY_ID = 'private_key_id'
_BACKEND = backends.default_backend()
_PADDING = padding.PKCS1v15()
_SHA256 = hashes.SHA256()


def _parse_service_account():
    with open(URL_SIGNER_SERVICE_ACCOUNT_FILE, 'r', encoding='utf-8') as json_file:
        return json.load(json_file)


_SERVICE_ACCOUNT_INFO = _parse_service_account()


class CryptographySigner(crypt.Signer):
    """Signs messages with a cryptography ``PKey`` private key.

    Args:
        private_key (cryptography.hazmat.backends.openssl.rsa._RSAPrivateKey):
            The private key to sign with.
        key_id (str): Optional key ID used to identify this private key. This
            can be useful to associate the private key with its associated
            public key or certificate.
    """

    def __init__(self, private_key, key_id=None):
        self._key = private_key
        self._key_id = key_id

    @property
    def key_id(self):
        """Optional[str]: The key ID used to identify this private key."""
        return self._key_id

    def sign(self, message):
        """Signs a message.

        Args:
            message (Union[str, bytes]): The message to be signed.

        Returns:
            bytes: The signature of the message.
        """
        message = _helpers.to_bytes(message)
        return self._key.sign(
            message, _PADDING, _SHA256)

    @classmethod
    def from_string(cls, key, key_id=None):
        """Construct a Signer instance from a private key in PEM format.

        Args:
            key (Union[bytes, str]): Private key in PEM format.
            key_id (str): An optional key id used to identify the private key.

        Returns:
            google.auth.crypt.CryptographySigner: The constructed signer.

        Raises:
            ValueError: If ``key`` is not ``bytes`` or ``str`` (unicode).
            UnicodeDecodeError: If ``key`` is ``bytes`` but cannot be decoded
                into a UTF-8 ``str``.
            ValueError: If ``cryptography`` "Could not deserialize key data."
        """
        message = _helpers.to_bytes(key)
        private_key = serialization.load_pem_private_key(
            message, password=None, backend=_BACKEND)
        return cls(private_key, key_id=key_id)

    @classmethod
    def from_service_account_info(cls, info):
        """Creates a Signer instance instance from a dictionary.

        The dictionary (``info``) is expecected to contain service account
        information in Google format.

        Args:
            info (Mapping[str, str]): The service account info in Google
                format.

        Returns:
            google.auth.crypt.CryptographySigner: The constructed signer.

        Raises:
            ValueError: If the info is not in the expected format.
        """
        if _JSON_FILE_PRIVATE_KEY not in info:
            raise ValueError(
                'The private_key field was not found in the service account '
                'info.')

        return cls.from_string(
            info[_JSON_FILE_PRIVATE_KEY],
            info.get(_JSON_FILE_PRIVATE_KEY_ID))

    @classmethod
    def from_service_account_file(cls, filename):
        """Creates a Signer instance from a JSON file.

        The ``.json`` file is expected to contain information in Google format
        describing a service account.

        Args:
            filename (str): The path to the service account ``.json`` file.

        Returns:
            google.auth.crypt.CryptographySigner: The constructed signer.
        """
        with io.open(filename, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)

        return cls.from_service_account_info(data)


class CloudStorageURLSigner(object):
    """Contains methods for generating signed URLs for Google Cloud Storage."""

    DEFAULT_GCS_API_ENDPOINT = 'https://storage.googleapis.com'

    def __init__(self, gcs_api_endpoint=None, expiration=None):
        """Creates a CloudStorageURLSigner that can be used to access signed URLs.
    Args:
      gcs_api_endpoint: Base URL for GCS API. Default is 'https://storage.googleapis.com'
      expiration: An instance of datetime.datetime containing the time when the
                  signed URL should expire.
    """
        self.gcs_api_endpoint = gcs_api_endpoint or self.DEFAULT_GCS_API_ENDPOINT
        self.expiration = expiration or (datetime.datetime.now() +
                                         datetime.timedelta(days=1))
        self.expiration = int(time.mktime(self.expiration.timetuple()))
        self.client_id_email = _SERVICE_ACCOUNT_INFO['client_email']
        self.signer = CryptographySigner.from_service_account_info(_SERVICE_ACCOUNT_INFO)

    def _make_signature_string(self, verb, path, content_md5, content_type):
        """Creates the signature string for signing according to GCS docs."""
        signature_string = ('{verb}\n'
                            '{content_md5}\n'
                            '{content_type}\n'
                            '{expiration}\n'
                            '{resource}')
        return signature_string.format(verb=verb,
                                       content_md5=content_md5,
                                       content_type=content_type,
                                       expiration=self.expiration,
                                       resource=path)

    def _sign(self, verb, path, content_type='', content_md5=''):
        """Forms and returns the full signed URL to access GCS."""
        base_url = '%s%s' % (self.gcs_api_endpoint, path)
        signature_string = self._make_signature_string(verb, path, content_md5,
                                                       content_type)
        signature = quote_plus(b64encode(self.signer.sign(signature_string)))
        return "{}?GoogleAccessId={}&Expires={}&Signature={}".format(base_url, self.client_id_email,
                                                                     str(self.expiration), signature)

    def sign(self, url):
        if self.is_stored_on_google_cloud_storage(url):
            parsed_url = urlparse(url)
            return self._sign('GET', parsed_url.path)
        return url

    @staticmethod
    def is_stored_on_google_cloud_storage(url):
        return "storage.cloud.google.com" in url


