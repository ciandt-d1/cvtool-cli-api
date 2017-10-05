import os

URL_SIGNER_SERVICE_ACCOUNT_FILE = os.environ.get('URL_SIGNER_SERVICE_ACCOUNT_FILE',
                                                 '/var/run/secret/cloud.google.com/service-account.json')
ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL', 'http://elasticsearch:9200')
IMAGE_INGESTION_PIPELINE_URI = os.environ.get('IMAGE_INGESTION_PIPELINE_URI', None)
IMAGE_HASHES_API_HOST = os.environ.get('IMAGE_HASHES_API_HOST', None)
DEBUG = os.environ.get('DEBUG', None)
