import os
from aiocache import cached
from fastapi import FastAPI, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from functools import lru_cache

from db import get_latest
from info import get_diagnostic_info

API_KEY = os.getenv("API_KEY")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate API Key"
        )
    return api_key

app = FastAPI()

@app.get("/info")
async def info():
    log_path = os.getenv("LOG_PATH") or ""
    return await get_diagnostic_info(log_path=log_path)

@app.get("/latest")
@cached(ttl=10)
async def latest(api_key: str = Security(get_api_key)):
    db_path = os.getenv("DB_PATH") or ""
    return {'latest': await get_latest(db_path=db_path)}
