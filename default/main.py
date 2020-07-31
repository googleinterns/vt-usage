import aiohttp
import certifi
import logging
import re
import ssl
from fastapi import FastAPI, Request, Form, HTTPException, Header
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from google.cloud import ndb
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
                    json = await resp.json()
                    json['api_key'] = user.apikey
                    if resp.status != 200:
                        logging.error(resp.text())
                        raise HTTPException(400, 'Bad request')
                    async with httpSession.post(user.webhook, json=json, ssl=ssl_context) as post:
                        post_response = await post.text()
                        if post.status != 200:
                            error_msg = 'Post to webhook failed with {}: {}'.format(post.status, post_response)
                            logging.error(error_msg)
                            raise HTTPException(400, 'Bad request')
        return 'Success'
