from fastapi import FastAPI, APIRouter, Depends, status
from functools import lru_cache
from .config import Settings
from .gtfx_flex_validator import GTFSFlexValidator
from .publisher import send

app = FastAPI()

prefix_router = APIRouter(prefix='/health')


@lru_cache()
def get_settings():
    return Settings()


@app.on_event('startup')
async def startup_event(settings: Settings = Depends(get_settings)) -> None:
    GTFSFlexValidator()


@app.get('/', status_code=status.HTTP_200_OK)
@prefix_router.get('/', status_code=status.HTTP_200_OK)
def root():
    return "I'm healthy !!"


@app.get('/ping', status_code=status.HTTP_200_OK)
@app.post('/ping', status_code=status.HTTP_200_OK)
@prefix_router.get('/ping', status_code=status.HTTP_200_OK)
@prefix_router.post('/ping', status_code=status.HTTP_200_OK)
def ping():
    return "I'm healthy !!"


@app.post('/publish', status_code=status.HTTP_200_OK)
@app.get('/publish', status_code=status.HTTP_200_OK)
def publish(settings: Settings = Depends(get_settings)):
    message_id = send(settings=settings)
    return f'Published message with Message ID: {message_id}'


app.include_router(prefix_router)
