from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, utils
from datetime import datetime
from fastapi import FastAPI, Header, HTTPException, status, Response, Body
from fastapi.encoders import jsonable_encoder
from google.cloud import logging, ndb, secretmanager_v1 as secretmanager
from typing import Optional, Dict

from models import VTAPI, APIKey, APIKeyEmail, UserEmail, AuthUser

import base64
import json
import jwt
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


def get_secret(secret):
    client = secretmanager.SecretManagerServiceClient()
    version = client.secret_version_path('virustotal-step-2020', secret, '1')
    return client.access_secret_version(version).payload.data.decode()


@app.post("/auth/")
async def auth(request: AuthUser):
    authorized_key = get_secret('access_key')

    if request.access_key != authorized_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Unknown key")

    jwt_secret = get_secret('jwt_secret')

    res = jwt.encode({'api_key': request.vt_key, 'issued': datetime.now(
    ).isoformat()}, jwt_secret, algorithm='HS256').decode()
    return res


@app.post("/query-results/")
async def send_query_results(request: VTAPI):
    try:
        decoded = jwt.decode(request.jwt_token, get_secret(
            'jwt_secret'), algorithms=['HS256'])
    except jwt.exceptions.InvalidSignatureError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden")

    if (datetime.now() - datetime.fromisoformat(decoded['issued'])).seconds > 60:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Token expired")

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


@app.post("/email-address/",
          responses={status.HTTP_201_CREATED: {}})
async def set_email(content: APIKeyEmail, response: Response):
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
