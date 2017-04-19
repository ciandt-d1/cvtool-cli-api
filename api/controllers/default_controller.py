from elasticsearch import Elasticsearch

ES = Elasticsearch('http://elasticsearch:9200')
INDEX_NAME = 'kingpick'
TENANT_DOC_TYPE = 'tenant'

def setup():
    """
    setup
    Setup basic infrastructure

    :rtype: None
    """

    body = {
        "settings": {
            "number_of_shards": 10 
        },
        "mappings": {
            TENANT_DOC_TYPE: {
                "properties": {
                    "name": { 
                        "type":  "text",
                        "index": True
                    },
                    "description": { 
                        "type":  "text",
                        "index": True
                    },
                    "settings": { 
                        "dynamic": True,
                        "properties": {}
                    }                    
                }
            },

            "project": {
                "properties": {
                    
                    "tenant_id": { 
                        "type":  "keyword",
                        "index": True
                    },

                    "name": { 
                        "type":  "text",
                        "index": True
                    },
                    "description": { 
                        "type":  "text",
                        "index": True
                    }
                }
            },

            "job": {
                "properties": {
                    "tenant_id": { 
                        "type":  "keyword",
                        "index": True
                    },
                    
                    "project_id": { 
                        "type":  "keyword",
                        "index": True
                    },

                    "type": { 
                        "type":  "keyword",
                        "index": True
                    },

                    "status": { 
                        "type":  "keyword",
                        "index": True
                    },

                    "exit_status": { 
                        "type":  "keyword",
                        "index": True
                    },

                    "exit_message": { 
                        "type":  "keyword",
                        "index": True
                    },

                    "create_time": { 
                        "type":  "date",
                        "index": True
                    },
                    
                    "start_time": { 
                        "type":  "date",
                        "index": True
                    },
                    
                    "end_time": { 
                        "type":  "date",
                        "index": True
                    },

                    "last_updated": { 
                        "type":  "date",
                        "index": True
                    },

                    "created_by": { 
                        "type":  "keyword",
                        "index": True
                    },

                    "parameters": {
                        "type": "object",
                        "dynamic": True
                    }
                    
                }
            },

            "job_step" : {
                "properties": {
                    "tenant_id": { 
                        "type":  "keyword",
                        "index": True
                    },
                    
                    "job_id": { 
                        "type":  "keyword",
                        "index": True
                    },

                    "step_name": { 
                        "type":  "keyword",
                        "index": True
                    },            

                    "status": { 
                        "type":  "keyword",
                        "index": True
                    },

                    "exit_status": { 
                        "type":  "keyword",
                        "index": True
                    },

                    "exit_message": { 
                        "type":  "keyword",
                        "index": True
                    },

                    "create_time": { 
                        "type":  "date",
                        "index": True
                    },
                    
                    "start_time": { 
                        "type":  "date",
                        "index": True
                    },
                    
                    "end_time": { 
                        "type":  "date",
                        "index": True
                    },

                    "last_updated": { 
                        "type":  "date",
                        "index": True
                    }
                }       
            },

            "image": {
                "properties": {

                    "tenant_id": { 
                        "type":  "keyword",
                        "index": True
                    },

                    "job_id": { 
                        "type":  "keyword",
                        "index": True
                    },

                    "project_id": { 
                        "type":  "keyword",
                        "index": True
                    },

                    "original_uri": { 
                        "type":  "text",
                        "index": True,
                        "fields": {
                            "raw": {
                                "type":  "keyword"
                            }
                        }
                    },
                    
                    "uri": {
                        "type":  "text",
                        "index": True,
                        "fields": {
                            "raw": {
                                "type":  "keyword"
                            }
                        }
                    },

                    "width": { 
                        "type":  "integer",
                        "index": True
                    },

                    "height": { 
                        "type":  "integer",
                        "index": True
                    },

                    "size": { 
                        "type":  "integer",
                        "index": True
                    },

                    "type": { 
                        "type":  "keyword",
                        "index": True
                    },

                    "annotations" : { 
                        "type" : "nested",
                        "properties": {
                            "key": { "type": "keyword"  },
                            "value": { "type": "keyword"  },
                            "status": { "type": "keyword" }
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
                            "parent_id": { "type": "keyword" }
                        }
                    }
                }        
            }
        }
    }
    
    ES.indices.delete_alias(index='*', name='_all', ignore=[404])
    ES.indices.delete(index='*', ignore=[404])
    ES.indices.create(index=INDEX_NAME, body=body, update_all_types=True)

    return 'Up and running!'

