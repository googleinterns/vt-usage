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

import os
import shutil
import uuid

import uvicorn
from fastapi import FastAPI, File, UploadFile, Request, status, HTTPException
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory='templates')

MEDIA_DIR = "media"


@app.get("/")
async def load_main_page(request: Request):
    return templates.TemplateResponse("form.html.jinja", {'request': request})


@app.post("/upload-file/")
async def upload_file(request: Request, file: UploadFile = File(...)):
    # TODO: Make sure that file isn't too big. @niedziol
    unique_name = uuid.uuid4().hex
    path = os.path.join(MEDIA_DIR, unique_name)

    with open(path, 'wb+') as destination:
        shutil.copyfileobj(file.file, destination)

    return templates.TemplateResponse("file_name.html.jinja",
                                      {"request": request, "name": unique_name})


@app.get("/{file_name}")
async def download_file(file_name: str):
    path = os.path.join(MEDIA_DIR, file_name)

    if not os.path.isfile(path):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="File not found.")

    return FileResponse(path)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, debug=True, reload=True)
