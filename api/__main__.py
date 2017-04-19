#!/usr/bin/env python3
import os
import connexion
import logging

from .encoder import JSONEncoder

HOST = os.getenv('HOST', '0.0.0.0')
PORT = os.getenv('PORT', 8080)
DEBUG = os.getenv('DEBUG', False)

es_tracer = logging.getLogger('elasticsearch.trace')
es_tracer.propagate = False
es_tracer.setLevel(logging.DEBUG)
es_tracer_handler = logging.StreamHandler()
es_tracer.addHandler(es_tracer_handler)

if __name__ == '__main__':
    app = connexion.App(__name__, specification_dir='./swagger/')
    app.app.json_encoder = JSONEncoder
    app.add_api('swagger.yaml', arguments={'title': 'Auth token provider'})
    app.run(port=PORT, debug=bool(DEBUG), host=HOST)
