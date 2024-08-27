import logging
import asyncio as aio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer

from router import router
from monitoring.sensors import serve_sensors


logger = logging.getLogger(__name__)


# https://stackoverflow.com/questions/77674952/how-to-run-fastapi-app-and-tcp-server-as-async-tasks-within-the-same-fastapi-eve
@asynccontextmanager
async def startup_event(app: FastAPI):
    aio.create_task(serve_sensors())
    logger.info("Server started listening to sensors")

    yield


app = FastAPI(lifespan=startup_event)

http_bearer = HTTPBearer()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8081",
    "http://localhost:8082",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:8081",
    "http://127.0.0.1:8082",
    "http://127.0.0.1",
    "http://localhost/",
    "http://localhost:8080/",
    "http://localhost:8081/",
    "http://localhost:8082/",
    "http://127.0.0.1:8080/",
    "http://127.0.0.1:8081/",
    "http://127.0.0.1:8082/",
    "http://127.0.0.1/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Set-Cookie"],
)

# https://stackoverflow.com/questions/76231804/fastapi-how-to-modularize-code-into-multiple-files-with-access-to-app-decorators
app.include_router(router)
