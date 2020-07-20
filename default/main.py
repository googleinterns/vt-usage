import re
import requests
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


@app.get('/run_queries/')  # TODO: test it
async def run_queries(x_appengine_cron: Optional[str] = Header(None)):
    if x_appengine_cron != 'true':
        raise HTTPException(403, 'Access forbidden')
    
    with client.context():
        for user in models.Userdata.query():
            vt_data = requests.get('https://www.virustotal.com/api/v3/intelligence/search?query={query}'.format(query=user.vt_query),
                                   headers={'x-apikey': user.apikey}).json()
            requests.post(user.webhook, vt_data)
        return 'Success'
