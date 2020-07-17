from enum import Enum
from fastapi import FastAPI, Request, Header, HTTPException, Body
from google.cloud import ndb
from pydantic import BaseModel, validator
from typing import List, Optional, Dict, Union
from validate_email import validate_email

app = FastAPI()
client = ndb.Client()


@app.get("/")
async def root():
    return {"data": "Hello World"}


class VTType(str, Enum):
    file = 'file'
    url = 'url'
    domain = 'domain'
    ip_address = 'ip_address'


class VTData(BaseModel):
    attributes: Dict
    id: str
    links: Dict
    type: VTType


class VTAPI(BaseModel):
    data: List[VTData]
    links: Dict
    meta: Dict


@app.post("/query-results/")
async def query_results(data: VTAPI, x_appengine_inbound_appid: Optional[str] = Header(None)):
    if x_appengine_inbound_appid != 'virustotal-step-2020':
        raise HTTPException(status_code=403, detail="Access forbidden")

    return data


class Email(BaseModel):
    api_key: str
    email: str

    @validator('api_key')
    def api_key_validator(cls, v):
        if not v.isalnum():
            raise ValueError("API key must be alphanumeric!")
        return v

    @validator('email')
    def email_validator(cls, v):
        if not validate_email(email_address=v,
                              check_regex=True,
                              check_mx=True,
                              debug=True):
            raise ValueError("Email address is not valid!")
        return v


@app.put("/email-address/")
async def set_email(data: Email):
    return data
