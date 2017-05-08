#!/usr/bin/env python3

import connexion
import logging

import sys

from api.encoder import JSONEncoder

from google.cloud.logging.handlers.container_engine import ContainerEngineHandler

app = connexion.App(__name__, specification_dir='./api/swagger/')
app.app.json_encoder = JSONEncoder
app.add_api('swagger.yaml', arguments={'title': 'Provides APIs for tenant maintenance'})

def main():
    import os
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = os.getenv('PORT', 8080)
    DEBUG = os.getenv('DEBUG', False)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(ContainerEngineHandler(sys.stdout))

    app.run(port=PORT, debug=DEBUG, host=HOST)

if  __name__ =='__main__':
    main()
