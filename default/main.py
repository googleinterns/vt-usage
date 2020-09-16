# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import aiohttp
import base64
import certifi
import hashlib
import json
import logging
import re
import ssl
from fastapi import FastAPI, Request, Form, HTTPException, Header
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from google.cloud import ndb, secretmanager_v1 as secretmanager
from typing import Optional

import models

app = FastAPI()

app.mount('/static', StaticFiles(directory='static'), name='static')

templates = Jinja2Templates(directory='templates')

ssl_context = ssl.create_default_context(cafile=certifi.where())


@app.get('/')
async def index(request: Request):
    return templates.TemplateResponse("form.html", {'request': request, 'content': 'Save your credentials'})


@app.post('/userdata/')
async def userdata(request: Request, apikey: str = Form(...), webhook: str = Form(...), vt_query: str = Form(...)):
    client = ndb.Client()
    re_url = re.compile(r'[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)')
    if not re_url.search(webhook):
        raise HTTPException(400, 'Bad request')
    with client.context():
        task = models.Userdata(apikey=apikey, webhook=webhook, vt_query=vt_query)
        task.put()
    return templates.TemplateResponse("index.html", {'request': request, 'content': 'Your answer was successfully saved'})


def get_secret(secret):
    client = secretmanager.SecretManagerServiceClient()
    version = client.secret_version_path('virustotal-step-2020', secret, '1')
    return client.access_secret_version(version).payload.data.decode()


@app.get('/run_queries/')
async def run_queries(x_appengine_cron: Optional[str] = Header(None)):
    client = ndb.Client()
    if x_appengine_cron != 'true':
        raise HTTPException(403, 'Access forbidden')

    with client.context():
        for user in models.Userdata.query():
            async with aiohttp.ClientSession() as httpSession:

                # Run VT query.
                async with httpSession.get(
                        f'https://www.virustotal.com/api/v3/intelligence/search?query={user.vt_query}',
                        headers={'x-apikey': user.apikey},
                        ssl=ssl_context) as vt_resp:

                    payload = {'api_key': user.apikey}
                    payload.update(await vt_resp.json())

                    if vt_resp.status != 200:
                        logging.error(f'VT query failed with {vt_resp.status}: {vt_resp.text()}')
                        raise HTTPException(400, 'Bad request')

                    # Auth to webhook, get JWT token.
                    async with httpSession.post('https://webhook-dot-virustotal-step-2020.ew.r.appspot.com/auth/',
                                                json={'access_key': get_secret('access_key'), 'vt_key': user.apikey},
                                                ssl=ssl_context) as auth_resp:

                        jwt_token = await auth_resp.text()
                        payload['jwt_token'] = jwt_token.strip('"')  # Webhook sends token with quotes.

                        if auth_resp.status != 200:
                            logging.error(f'Authentication on webhook failed with {auth_resp.status}: {auth_resp.text()}')
                            raise HTTPException(403, 'Authentication failed')

                        # Send data with JWT to webhook.
                        async with httpSession.post(user.webhook, json=payload, ssl=ssl_context) as webhook_resp:

                            result = await webhook_resp.text()

                            if webhook_resp.status != 200:
                                logging.error(f'Post to webhook failed with {webhook_resp.status}: {result}')
                                raise HTTPException(400, 'Bad request')

    return 'Success'
