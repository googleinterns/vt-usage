from fastapi import FastAPI, Request, Header, HTTPException, Body
from pydantic import BaseModel
from typing import List, Optional, Dict, Union

app = FastAPI()


@app.get("/")
async def root():
    return {"data": "Hello World"}


class VTAPI(BaseModel):
  data: Union[str, List, Dict]
  links: Optional[Dict]
  meta: Optional[Dict]

@app.post("/query-results/")
async def query_results(data: VTAPI, x_appengine_inbound_appid: Optional[str] = Header(None)):
    if x_appengine_inbound_appid != 'virustotal-step-2020':
        raise HTTPException(status_code=403, detail="Access forbidden")

    return data
