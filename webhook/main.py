from fastapi import FastAPI, Header, HTTPException, status, Response, Body
from google.cloud import ndb
from typing import Optional, Dict

from models import VTAPI, APIKey, APIKeyEmail, UserEmail

import smtplib

app = FastAPI()
client = ndb.Client()


@app.get("/")
async def root():
    return {"data": "Hello World"}


@app.post("/query-results/")
async def send_query_results(request: VTAPI,
                             x_appengine_inbound_appid: Optional[str] = Header(None)):
    if x_appengine_inbound_appid != 'virustotal-step-2020':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden")

    email = None
    with client.context():
        email = ndb.Key("UserEmail", request.api_key).get()

    if email is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="API Key is not valid")


@app.post("/email-address/")
async def set_email(response: Response, content: APIKeyEmail):
    # TODO Check why documentation is not generating correct response code_status.
    def update_email(api_key: str, email: str, response: Response):
        email_obj = ndb.Key("UserEmail", api_key).get()
        if email_obj is None:
            email_obj = UserEmail(api_key=ndb.Key(
                "UserEmail", api_key), email=email)
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
