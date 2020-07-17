import re
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from google.cloud import ndb

from default import models

app = FastAPI()

app.mount('/static', StaticFiles(directory='static'), name='static')

templates = Jinja2Templates(directory='templates')

client = ndb.Client()


@app.get('/')
async def index(request: Request):
    return templates.TemplateResponse("form.html", {'request': request, 'content': 'Save your credentials'})


@app.post('/userdata/')
async def userdata(request: Request, apikey: str = Form(...), webhook: str = Form(...)):
    re_url = re.compile(r'[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)')
    if not re_url.search(webhook):
        raise HTTPException(400, 'Bad request')
    with client.context():
        task = models.Userdata(apikey=apikey, webhook=webhook)
        task.put()
    return templates.TemplateResponse("index.html", {'request': request, 'content': 'Your answer was successfully saved'})
