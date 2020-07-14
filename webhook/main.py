from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/")
async def root():
    return {"data": "Hello World"}
