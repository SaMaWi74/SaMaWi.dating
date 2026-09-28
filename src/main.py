from fastapi import FastAPI, Request
from workers import asgi

app = FastAPI(title="SaMaWi Dating", version="0.1.0")
Default = asgi.entrypoint(app)


@app.get("/")
async def root():
    return {
        "name": "SaMaWi Dating",
        "status": "running",
        "production": "dating.samawi.co.uk",
    }


@app.get("/health")
async def health(request: Request):
    env = request.scope["env"]
    result = await env.DB.prepare("SELECT 1 AS ok").first()
    return {
        "status": "healthy" if result and result.ok == 1 else "degraded",
        "database": "D1",
    }
