from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, utils
from fastapi import FastAPI, Header, HTTPException, status, Response, Body
from fastapi.encoders import jsonable_encoder
from google.cloud import logging, ndb, kms
from typing import Optional, Dict

from models import VTAPI, APIKey, APIKeyEmail, UserEmail

import base64
import json
import logging as log
import hashlib

app = FastAPI()
client = ndb.Client()


def setup_cloud_logging():
    logger = logging.Client()
    logger.get_default_handler()
    logger.setup_logging()


setup_cloud_logging()


@app.get("/")
async def root():
    return {"data": "Hello World"}


def verify_asymmetric_ec(project_id, location_id, key_ring_id, key_id, version_id, message, signature):
    message_bytes = message.encode('utf-8')
    signature = base64.b64decode(signature.encode())

    client = kms.KeyManagementServiceClient()

    key_version_name = client.crypto_key_version_path(project_id, location_id, key_ring_id, key_id, version_id)

    public_key = client.get_public_key(request={'name': key_version_name})

    pem = public_key.pem.encode('utf-8')
    ec_key = serialization.load_pem_public_key(pem, default_backend())
    hash_ = hashlib.sha256(message_bytes).digest()

    sha256 = hashes.SHA256()
    ec_key.verify(signature, hash_, ec.ECDSA(utils.Prehashed(sha256)))  # raises InvalidSignature


@app.post("/query-results/")
async def send_query_results(request: VTAPI,
                             signature: Optional[str] = Header(None)):
    try:
        verify_asymmetric_ec('virustotal-step-2020', 'global', 'webhook-keys', 'webhook-sign', 1, json.dumps(jsonable_encoder(request)), signature)
    except InvalidSignature:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden")

    email = None
    with client.context():
        email_row = ndb.Key("UserEmail", request.api_key).get()

        if email_row is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="API Key is not valid")
        else:
            email = email_row.email

    log.info("Send an email to {}.\nBody:\n{}".format(
        email, json.dumps(jsonable_encoder(request.data))))


@app.post("/email-address/")
async def set_email(content: APIKeyEmail, response: Response):
    # TODO Check why documentation is not generating correct response code_status.
    def update_email(api_key: str, email: str, response: Response):
        email_obj = ndb.Key("UserEmail", api_key).get()
        if email_obj is None:
            email_obj = UserEmail(id=api_key, email=email)
            response.status_code = status.HTTP_201_CREATED
        else:
            email_obj.email = email
            response.status_code = status.HTTP_200_OK

        email_obj.put()

    with client.context():
        ndb.transaction(lambda: update_email(
            content.api_key, content.email, response))


@app.delete("/email-address/")
async def delete_email(api_key: APIKey):
    with client.context():
        ndb.Key("UserEmail", api_key.api_key).delete()
