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

client = ndb.Client()
ssl_context = ssl.create_default_context(cafile=certifi.where())


@app.get('/')
async def index(request: Request):
    return templates.TemplateResponse("form.html", {'request': request, 'content': 'Save your credentials'})


@app.post('/userdata/')
async def userdata(request: Request, apikey: str = Form(...), webhook: str = Form(...), vt_query: str = Form(...)):
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
    if x_appengine_cron != 'true':
        raise HTTPException(403, 'Access forbidden')

    with client.context():
        for user in models.Userdata.query():
            async with aiohttp.ClientSession() as httpSession:
                async with httpSession.get(
                        'https://www.virustotal.com/api/v3/intelligence/search?query={query}'.format(query=user.vt_query),
                        headers={'x-apikey': user.apikey},
                        ssl=ssl_context
                    ) as resp:
                    js = {'api_key': user.apikey}
                    js.update(await resp.json())
                    
                    if resp.status != 200:
                        logging.error(resp.text())
                        raise HTTPException(400, 'Bad request')

                    async with httpSession.post('https://webhook-dot-virustotal-step-2020.ew.r.appspot.com/',
                                                json={'access_key': get_secret('access_key'), 'vt_key': user.apikey}, ssl=ssl_context) as auth_res:
                        js['jwt_token'] = await auth_res.text()
                        js['jwt_token'] = js['jwt_token'][1:-1]  # I have no idea why does webhook send a key with quotes
                        if auth_res.status != 200:
                            logging.error('Authentication on webhook failed')
                            raise HTTPException(500, 'Internal server error')
                        async with httpSession.post(user.webhook, json=js, ssl=ssl_context) as post:
                            post_response = await post.text()
                            if post.status != 200:
                                error_msg = 'Post to webhook failed with {}: {}'.format(post.status, post_response)
                                logging.error(error_msg)
                                raise HTTPException(400, 'Bad request')
        return 'Success'
