import os

ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL', 'http://elasticsearch:9200')
IMAGE_INGESTION_PIPELINE_URI = os.environ.get('IMAGE_INGESTION_PIPELINE_URI', None)
