from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from google.cloud import datastore

app = FastAPI()

app.mount('/static', StaticFiles(directory='static'), name='static')

templates = Jinja2Templates(directory='templates')

datastore_client = datastore.Client()


@app.get('/')
async def index(request: Request):
    return templates.TemplateResponse("form.html", {'request': request, 'content': 'Hello, world! =)'})


@app.post('/userdata/')
async def userdata(request: Request, apikey: str = Form(...), webhook: str = Form(...)):
    task = datastore.Entity(datastore_client.key('userdata'))
    task.update({
        'apikey': apikey,
        'webhook': webhook,
    })
    datastore_client.put(task)
    return templates.TemplateResponse("index.html", {'request': request, 'content': 'Your answer successfully saved'})