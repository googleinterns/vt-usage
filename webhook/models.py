# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from enum import Enum
from google.cloud import ndb
from pydantic import BaseModel, validator
from typing import List, Dict

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
        regex = r"[a-z0-9\.\-]+[@]\w+[.]\w+$"

        if not re.match(regex, v):
            raise ValueError("Email address is not valid!")
        return v


class UserEmail(ndb.Model):
    email = ndb.StringProperty()


class AuthUser(BaseModel):
    access_key: str
    vt_key: str
