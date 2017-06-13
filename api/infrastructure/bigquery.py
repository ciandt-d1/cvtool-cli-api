import uuid

import logging

import time
from google.cloud import bigquery
from google.cloud.bigquery import SchemaField


def _bounding_poly(name='boundingPoly'):
    return SchemaField(name, 'RECORD', mode='NULLABLE', fields=[
        SchemaField('vertices', 'RECORD', mode='REPEATED', fields=[
            SchemaField('x', 'INTEGER', mode='NULLABLE'),
            SchemaField('y', 'INTEGER', mode='NULLABLE')
        ])
    ])


def _entity_annotation(name):
    return SchemaField(name, 'RECORD', mode='REPEATED', fields=[
        SchemaField('mid', 'STRING', mode='NULLABLE'),
        SchemaField('locale', 'STRING', mode='NULLABLE'),
        SchemaField('description', 'STRING', mode='NULLABLE'),
        SchemaField('topicality', 'FLOAT', mode='NULLABLE'),
        SchemaField('score', 'FLOAT', mode='NULLABLE'),
        SchemaField('confidence', 'FLOAT', mode='NULLABLE'),
        SchemaField('properties', 'RECORD', mode='REPEATED', fields=[
            SchemaField('value', 'STRING', mode='NULLABLE'),
            SchemaField('name', 'STRING', mode='NULLABLE')
        ]),
        SchemaField('locations', 'RECORD', mode='REPEATED', fields=[
            SchemaField('latLng', 'RECORD', mode='NULLABLE', fields=[
                SchemaField('latitude', 'FLOAT', mode='NULLABLE'),
                SchemaField('longitude', 'FLOAT', mode='NULLABLE')
            ])
        ]),
        _bounding_poly()
    ])


def _property():
    return SchemaField('property', 'RECORD', mode='NULLABLE', fields=[
        SchemaField('detectedLanguages', 'RECORD', mode='REPEATED', fields=[
            SchemaField('languageCode', 'STRING', mode='NULLABLE'),
            SchemaField('confidence', 'FLOAT', mode='NULLABLE')
        ]),
        SchemaField('detectedBreak', 'RECORD', mode='NULLABLE', fields=[
            SchemaField('type', 'STRING', mode='NULLABLE'),
            SchemaField('isPrefix', 'BOOLEAN', mode='NULLABLE')
        ])
    ])


SCHEMA = [
    SchemaField('project_id', 'STRING', mode='NULLABLE'),
    SchemaField('id', 'STRING', mode='REQUIRED'),
    SchemaField('version', 'STRING', mode='REQUIRED'),
    SchemaField('job_id', 'STRING', mode='REQUIRED'),
    SchemaField('original_uri', 'STRING', mode='NULLABLE'),
    SchemaField('exif_annotations', 'RECORD', mode='REPEATED', fields=[
        SchemaField('key', 'STRING', mode='REQUIRED'),
        SchemaField('value', 'STRING', mode='REQUIRED')
    ]),
    SchemaField('vision_annotations', 'RECORD', mode='NULLABLE', fields=[

        SchemaField('safeSearchAnnotation', 'RECORD', mode='NULLABLE', fields=[
            SchemaField('adult', 'STRING', mode='NULLABLE'),
            SchemaField('spoof', 'STRING', mode='NULLABLE'),
            SchemaField('medical', 'STRING', mode='NULLABLE'),
            SchemaField('violence', 'STRING', mode='NULLABLE')
        ]),

        _entity_annotation('labelAnnotations'),

        _entity_annotation('landmarkAnnotations'),

        _entity_annotation('logoAnnotations'),

        _entity_annotation('textAnnotations'),

        SchemaField('imagePropertiesAnnotation', 'RECORD', mode='NULLABLE', fields=[
            SchemaField('dominantColors', 'RECORD', mode='NULLABLE', fields=[
                SchemaField('colors', 'RECORD', mode='REPEATED', fields=[
                    SchemaField('pixelFraction', 'FLOAT', mode='NULLABLE'),
                    SchemaField('score', 'FLOAT', mode='NULLABLE'),
                    SchemaField('color', 'RECORD', mode='NULLABLE', fields=[
                        SchemaField('red', 'FLOAT', mode='NULLABLE'),
                        SchemaField('green', 'FLOAT', mode='NULLABLE'),
                        SchemaField('blue', 'FLOAT', mode='NULLABLE'),
                        SchemaField('alpha', 'FLOAT', mode='NULLABLE')
                    ]),
                ])
            ])
        ]),

        SchemaField('faceAnnotations', 'RECORD', mode='REPEATED', fields=[
            SchemaField('tiltAngle', 'FLOAT', mode='NULLABLE'),
            SchemaField('underExposedLikelihood', 'STRING', mode='NULLABLE'),
            SchemaField('joyLikelihood', 'STRING', mode='NULLABLE'),
            SchemaField('surpriseLikelihood', 'STRING', mode='NULLABLE'),
            SchemaField('angerLikelihood', 'STRING', mode='NULLABLE'),
            SchemaField('headwearLikelihood', 'STRING', mode='NULLABLE'),
            SchemaField('blurredLikelihood', 'STRING', mode='NULLABLE'),
            SchemaField('sorrowLikelihood', 'STRING', mode='NULLABLE'),
            SchemaField('rollAngle', 'FLOAT', mode='NULLABLE'),
            SchemaField('fdBoundingPoly', 'RECORD', mode='NULLABLE', fields=[
                SchemaField('vertices', 'RECORD', mode='REPEATED', fields=[
                    SchemaField('x', 'INTEGER', mode='NULLABLE'),
                    SchemaField('y', 'INTEGER', mode='NULLABLE')
                ])
            ]),
            SchemaField('landmarkingConfidence', 'FLOAT', mode='NULLABLE'),
            SchemaField('landmarks', 'RECORD', mode='REPEATED', fields=[
                SchemaField('type', 'STRING', mode='NULLABLE'),
                SchemaField('position', 'RECORD', mode='NULLABLE', fields=[
                    SchemaField('x', 'FLOAT', mode='NULLABLE'),
                    SchemaField('y', 'FLOAT', mode='NULLABLE'),
                    SchemaField('z', 'FLOAT', mode='NULLABLE')

                ])
            ]),
            SchemaField('detectionConfidence', 'FLOAT', mode='NULLABLE'),
            SchemaField('panAngle', 'FLOAT', mode='NULLABLE'),
            SchemaField('boundingPoly', 'RECORD', mode='NULLABLE', fields=[
                SchemaField('vertices', 'RECORD', mode='REPEATED', fields=[
                    SchemaField('x', 'INTEGER', mode='NULLABLE'),
                    SchemaField('y', 'INTEGER', mode='NULLABLE')
                ])
            ])
        ]),

        SchemaField('cropHintsAnnotation', 'RECORD', mode='NULLABLE', fields=[
            SchemaField('cropHints', 'RECORD', mode='REPEATED', fields=[
                SchemaField('importanceFraction', 'FLOAT', mode='NULLABLE'),
                SchemaField('confidence', 'FLOAT', mode='NULLABLE'),
                SchemaField('boundingPoly', 'RECORD', mode='NULLABLE', fields=[
                    SchemaField('vertices', 'RECORD', mode='REPEATED', fields=[
                        SchemaField('x', 'INTEGER', mode='NULLABLE'),
                        SchemaField('y', 'INTEGER', mode='NULLABLE')
                    ])
                ])
            ])
        ]),

        SchemaField('fullTextAnnotation', 'RECORD', mode='NULLABLE', fields=[
            SchemaField('text', 'STRING', mode='NULLABLE'),
            SchemaField('pages', 'RECORD', mode='REPEATED', fields=[
                SchemaField('width', 'INTEGER', mode='NULLABLE'),
                SchemaField('height', 'INTEGER', mode='NULLABLE'),
                _property(),
                SchemaField('blocks', 'RECORD', mode='REPEATED', fields=[
                    _bounding_poly('boundingBox'),
                    SchemaField('blockType', 'STRING', mode='NULLABLE'),
                    _property(),
                    SchemaField('paragraphs', 'RECORD', mode='REPEATED', fields=[
                        _bounding_poly('boundingBox'),
                        _property(),
                        SchemaField('words', 'RECORD', mode='REPEATED', fields=[
                            _bounding_poly('boundingBox'),
                            _property(),
                            SchemaField('symbols', 'RECORD', mode='REPEATED', fields=[
                                _bounding_poly('boundingBox'),
                                _property(),
                                SchemaField('text', 'STRING', mode='NULLABLE')
                            ])
                        ])
                    ])
                ])
            ])
        ])
    ]
                )]

logger = logging.getLogger(__name__)

bq_client = bigquery.Client()


def load_table_from_json(tenant, source_uri, wait=False):
    dataset = bq_client.dataset(dataset_name=tenant.id, project=tenant.google_cloud_project)
    if not dataset.exists():
        dataset.create()

    bq_table = dataset.table('images', SCHEMA)

    if bq_table.exists():
        bq_table.delete()
    if not bq_table.exists():
        bq_table.create()

    job = bq_client.load_table_from_storage(str(uuid.uuid4()), bq_table, source_uri)
    job.source_format = 'NEWLINE_DELIMITED_JSON'
    job.write_disposition = 'WRITE_TRUNCATE'
    job.ignore_unknown_values = True

    logger.info('Starting job')
    job.begin()
    if wait:
        retry_count = 100
        while retry_count > 0 and job.state != 'DONE':
            retry_count -= 1
            time.sleep(10)
            logger.info('Reloading %s', job)
            job.reload()  # API call

    logger.info('%s', job)
    logger.info('%s, %s, %s, %s', job.name, job.job_type, job.created, job.state)

    return job
