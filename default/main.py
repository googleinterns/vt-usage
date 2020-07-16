from fastapi import FastAPI, Request, Form
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
    with client.context():
        task = models.Userdata(apikey=apikey, webhook=webhook)
        task.put()
    return templates.TemplateResponse("index.html", {'request': request, 'content': 'Your answer successfully saved'})
