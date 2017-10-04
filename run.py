#!/usr/bin/env python3

import logging
import sys

import connexion
from flask_cors import CORS
from google.cloud.logging.handlers.container_engine import ContainerEngineHandler

from api.encoder import JSONEncoder

root = logging.getLogger()
root.setLevel(logging.DEBUG)
root.addHandler(ContainerEngineHandler(sys.stdout))

app = connexion.App(__name__, specification_dir='./api/swagger/')
app.app.json_encoder = JSONEncoder
CORS(app.app)

app.add_api('swagger.yaml', arguments={'title': 'Aquila APIs'}, swagger_json=True)


def main():
    import os
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = os.getenv('PORT', 8080)
    DEBUG = os.getenv('DEBUG', False)

    app.run(port=PORT, debug=DEBUG, host=HOST)


if __name__ =='__main__':
    main()
