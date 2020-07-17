from enum import Enum
from fastapi import FastAPI, Request, Header, HTTPException, Body
from pydantic import BaseModel
from typing import List, Optional, Dict, Union

app = FastAPI()


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
