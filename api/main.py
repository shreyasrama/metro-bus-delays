import os
from aiocache import cached
from fastapi import FastAPI, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from db import get_calls, get_latest, get_delays
from info import get_diagnostic_info

# Set up API Key to be passed in via a header
API_KEY = os.getenv("API_KEY")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate API Key"
        )
    return api_key

# Create app object
app = FastAPI()

# region Routes

@app.get("/info", description="Returns log output and database size.")
async def info():
    log_path = os.getenv("LOG_PATH") or ""
    db_path = os.getenv("DB_PATH") or ""

    return await get_diagnostic_info(log_path=log_path, db_path=db_path)

@app.get("/latest", description="Returns all entries that have the most recent response_timestamp.")
@cached(ttl=60)
async def latest(api_key: str = Security(get_api_key)):
    db_path = os.getenv("DB_PATH") or ""

    return {'latest': await get_latest(db_path=db_path)}

@app.get("/calls/", description="Returns all bus calls within a specified date range.")
async def calls(start: str, end: str, api_key: str = Security(get_api_key)):
    db_path = os.getenv("DB_PATH") or ""

    return {'calls': await get_calls(db_path=db_path, start_date=start, end_date=end)}

@app.get("/delays/", description="Returns all bus calls within a specified date range and delay amount.")
async def delays(start: str, end: str, delay: int = 3, api_key: str = Security(get_api_key)):
    db_path = os.getenv("DB_PATH") or ""

    return {'delays': await get_delays(db_path=db_path, start_date=start, end_date=end, delay=delay)}

# endregion
