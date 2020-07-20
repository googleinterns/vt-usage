from fastapi import FastAPI, Header, HTTPException
from google.cloud import ndb
from typing import Optional, Dict

from models import VTAPI, EmailWrapper

app = FastAPI()
client = ndb.Client()


@app.get("/")
async def root():
    return {"data": "Hello World"}


@app.post("/query-results/")
async def query_results(data: VTAPI, x_appengine_inbound_appid: Optional[str] = Header(None)):
    if x_appengine_inbound_appid != 'virustotal-step-2020':
        raise HTTPException(status_code=403, detail="Access forbidden")

    return data


class UserEmail(ndb.Model):
    api_key: ndb.StringProperty
    email: ndb.StringProperty


@app.post("/email-address/")
async def set_email(content: EmailWrapper):

    return content
    # with client.context():
    #     UserEmail(api_key=api_key, email=email).put()
