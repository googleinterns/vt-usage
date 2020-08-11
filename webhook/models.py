from enum import Enum
from google.cloud import ndb
from pydantic import BaseModel, validator
from typing import List, Optional, Dict, Union

import re


class VTType(str, Enum):
    file = "file"
    url = "url"
    domain = "domain"
    ip_address = "ip_address"


class VTData(BaseModel):
    attributes: Dict
    id: str
    links: Dict
    type: VTType


class APIKey(BaseModel):
    api_key: str

    @validator("api_key")
    def api_key_validator(cls, v):
        if not v.isalnum():
            raise ValueError("API key must be alphanumeric!")
        return v


class VTAPI(APIKey):
    data: List[VTData]
    links: Dict
    meta: Dict
    jwt_token: str


class APIKeyEmail(APIKey):
    email: str

    @validator("email")
    def email_validator(cls, v):
        regex = "[a-z0-9\.\-]+[@]\w+[.]\w+$"

        if not re.match(regex, v):
            raise ValueError("Email address is not valid!")
        return v


class UserEmail(ndb.Model):
    email = ndb.StringProperty()


class AuthUser(BaseModel):
    access_key: str
    vt_key: str
