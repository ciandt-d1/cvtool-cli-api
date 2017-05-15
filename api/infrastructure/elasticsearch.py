from elasticsearch import Elasticsearch
from ..config import ELASTICSEARCH_URL

ES = Elasticsearch(ELASTICSEARCH_URL)
INDEX_NAME = 'cvtool'
TENANT_DOC_TYPE = 'tenant'
PROJECT_DOC_TYPE = 'project'
INDEX_BODY = {
    "settings": {
        "number_of_shards": 10
    },
    "mappings": {
        TENANT_DOC_TYPE: {
            "properties": {
                "name": {
                    "type": "text",
                    "index": True
                },
                "description": {
                    "type": "text",
                    "index": True
                },
                "settings": {
                    "dynamic": True,
                    "properties": {}
                }
            }
        },

        PROJECT_DOC_TYPE: {
            "properties": {

                "tenant_id": {
                    "type": "keyword",
                    "index": True
                },

                "name": {
                    "type": "text",
                    "index": True
                },
                "description": {
                    "type": "text",
                    "index": True
                }
            }
        },

        "job": {
            "properties": {
                "tenant_id": {
                    "type": "keyword",
                    "index": True
                },

                "project_id": {
                    "type": "keyword",
                    "index": True
                },

                "type": {
                    "type": "keyword",
                    "index": True
                },

                "status": {
                    "type": "keyword",
                    "index": True
                },

                "exit_status": {
                    "type": "keyword",
                    "index": True
                },

                "exit_message": {
                    "type": "keyword",
                    "index": True
                },

                "create_time": {
                    "type": "date",
                    "index": True
                },

                "start_time": {
                    "type": "date",
                    "index": True
                },

                "end_time": {
                    "type": "date",
                    "index": True
                },

                "last_updated": {
                    "type": "date",
                    "index": True
                },

                "created_by": {
                    "type": "keyword",
                    "index": True
                },

                "parameters": {
                    "type": "object",
                    "dynamic": True
                }

            }
        },

        "job_step": {
            "properties": {
                "tenant_id": {
                    "type": "keyword",
                    "index": True
                },

                "job_id": {
                    "type": "keyword",
                    "index": True
                },

                "step_name": {
                    "type": "keyword",
                    "index": True
                },

                "status": {
                    "type": "keyword",
                    "index": True
                },

                "exit_status": {
                    "type": "keyword",
                    "index": True
                },

                "exit_message": {
                    "type": "keyword",
                    "index": True
                },

                "create_time": {
                    "type": "date",
                    "index": True
                },

                "start_time": {
                    "type": "date",
                    "index": True
                },

                "end_time": {
                    "type": "date",
                    "index": True
                },

                "last_updated": {
                    "type": "date",
                    "index": True
                }
            }
        },

        "image": {
            "properties": {

                "tenant_id": {
                    "type": "keyword",
                    "index": True
                },

                "job_id": {
                    "type": "keyword",
                    "index": True
                },

                "original_uri": {
                    "type": "text",
                    "index": "not_analyzed",
                    "fields": {
                        "raw": {
                            "type": "keyword"
                        }
                    }
                },

                "uri": {
                    "type": "text",
                    "index": True,
                    "fields": {
                        "raw": {
                            "type": "keyword"
                        }
                    }
                },

                "width": {
                    "type": "integer",
                    "index": True
                },

                "height": {
                    "type": "integer",
                    "index": True
                },

                "size": {
                    "type": "integer",
                    "index": True
                },

                "type": {
                    "type": "keyword",
                    "index": True
                },

                "exif_annotations": {
                    "dynamic": True,
                    "properties": {}
                },

                "annotations": {
                    "type": "nested",
                    "properties": {
                        "key": {"type": "keyword"},
                        "value": {"type": "keyword"},
                        "status": {"type": "keyword"}
                    }
                }
            }
        },

        "image_hash": {
            "dynamic": True,
            "properties": {
                "metadata": {
                    "type": "object",
                    "dynamic": True,
                    "properties": {
                        "parent_id": {"type": "keyword"}
                    }
                }
            }
        }
    }
}
