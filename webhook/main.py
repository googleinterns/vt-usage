from fastapi import FastAPI, Header, HTTPException, status
from google.cloud import ndb
from typing import Optional, Dict

from models import VTAPI, EmailWrapper, UserEmail

app = FastAPI()
client = ndb.Client()


@app.get("/")
async def root():
    return {"data": "Hello World"}


@app.post("/query-results/")
async def query_results(data: VTAPI, x_appengine_inbound_appid: Optional[str] = Header(None)):
    if x_appengine_inbound_appid != 'virustotal-step-2020':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden")

    return data


@app.post("/email-address/")
async def set_email(content: EmailWrapper):
    with client.transaction():
        q = UserEmail.query(api_key=content.api_key)
        q_result = list(q.fetch())
        if len(q_result) > 1:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="There exist multiple rows with same api key")

        obj = None
        if len(q_result) == 0:
            obj = UserEmail(api_key=content.api_key, email=content.email)
        else:
            obj = q_result[0]
        
        obj.put()

    return content
