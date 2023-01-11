from typing import Union
import asyncio
from fastapi import FastAPI, APIRouter, Depends, status
from functools import lru_cache
from .config import Settings
from .gtfx_flex_validator import GTFSFlexValidator

app = FastAPI()

prefix_router = APIRouter(prefix='/health')

_job = None


@lru_cache()
def get_settings():
    return Settings()


@app.on_event('startup')
async def startup_event(settings: Settings = Depends(get_settings)) -> None:
    global _job
    _job = GTFSFlexValidator()


@app.on_event('shutdown')
async def shutdown_event() -> None:
    if _job and _job.monitor.is_running:
        _job.monitor.stop()


@prefix_router.get('/', status_code=status.HTTP_200_OK)
def root():
    return "I'm healthy !!"


@prefix_router.get('/ping', status_code=status.HTTP_200_OK)
@prefix_router.post('/ping', status_code=status.HTTP_200_OK)
def ping():
    return "I'm healthy !!"


app.include_router(prefix_router)
