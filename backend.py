import asyncio
import threading
import time
from datetime import datetime
import os
import logging
import requests
import pandas as pd
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api.routes import api_router

app = FastAPI()
app.mount("/static", StaticFiles(directory="frontend", html=True), name="frontend")

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backend")

# Incluir o router na aplicação
app.include_router(api_router)
