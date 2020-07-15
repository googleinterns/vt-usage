from fastapi import FastAPI, Request, Header, HTTPException

app = FastAPI()


@app.get("/")
async def root():
    return {"data": "Hello World"}


@app.post("/query-results/")
async def query_results(request: Request):
    if request.headers.get("X-Appengine-Inbound-Appid", None) != 'virustotal-step-2020':
        raise HTTPException(status_code=403, detail="Access forbidden")

    try:
        data = await request.json()
    except RuntimeError:
        data = None

    if "data" not in data:
        raise HTTPException(status_code=400, detail="Bad request")

    print(data)
