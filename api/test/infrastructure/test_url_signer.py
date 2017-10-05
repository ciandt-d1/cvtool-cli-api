# coding: utf-8

from unittest import TestCase

import os

os.environ["URL_SIGNER_SERVICE_ACCOUNT_FILE"] = "/secrets/aquila-url-signer-service-account.json"

from api.infrastructure.url_signer import CloudStorageURLSigner


class TestCloudStorageURLSigner(TestCase):
    def test_signed_download_url(self):
        signer = CloudStorageURLSigner()
        signed_url = signer.sign(
            'https://storage.cloud.google.com/fabito-kpick-df-experiments/costarica-moths/images/00-SRNP-10506-DHJ92503.jpg')
        print(signed_url)
