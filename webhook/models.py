from enum import Enum
from google.cloud import ndb
from pydantic import BaseModel, validator
from typing import List, Optional, Dict, Union

import re


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


class EmailWrapper(BaseModel):
    api_key: str
    email: str

    @validator("api_key")
    def api_key_validator(cls, v):
        if not v.isalnum():
            raise ValueError("API key must be alphanumeric!")
        return v

    @validator("email")
    def email_validator(cls, v):
        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'

        if not re.search(regex, v):
            raise ValueError("Email address is not valid!")
        return v


class UserEmail(ndb.Model):
    api_key: ndb.StringProperty
    email: ndb.StringProperty
