from fastapi import FastAPI, File, UploadFile, Request, Form, status, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse

import os
import shutil
import uvicorn
import uuid


app = FastAPI()

templates = Jinja2Templates(directory='templates')

MEDIA_DIR = "media"


@app.get("/")
async def load_main_page(request: Request):
    return templates.TemplateResponse("form.html", {'request': request})


@app.post("/upload-file/")
async def upload_file(file: UploadFile = File(...)):
    destination = open(os.path.join(MEDIA_DIR, uuid.uuid4().hex), 'wb+')
    shutil.copyfileobj(file.file, destination)
    destination.close()
    return {"filename": destination.name}


@app.get("/{file_name}")
async def download_file(file_name: str):
    path = os.path.join(MEDIA_DIR, file_name)

    if not os.path.isfile(path):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="File not found.")

    return FileResponse(os.path.join(MEDIA_DIR, file_name))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, debug=True, reload=True)
