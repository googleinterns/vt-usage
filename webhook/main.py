from fastapi import FastAPI, Header, HTTPException, status, Response
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


# @ndb.transactional
def update_email(dict: Dict):
    content = dict["content"]
    response = dict["response"]
    with client.context():
        email_obj = UserEmail.query(UserEmail.api_key == content.api_key).get()
        if email_obj is None:
            email_obj = UserEmail(api_key=content.api_key, email=content.email)
            response.status_code = status.HTTP_201_CREATED
        else:
            email_obj.email = content.email
            response.status_code = status.HTTP_200_OK

        email_obj.put()


@app.post("/email-address/")
async def set_email(content: EmailWrapper, response: Response):

    # Wrap content and response in dictionary because ndb.transactional needs one argument.
    update_email({"content": content, "response": response})
