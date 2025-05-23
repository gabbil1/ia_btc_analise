import asyncio
import threading
import time
from datetime import datetime
import os
import logging
import requests
import pandas as pd
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, APIRouter
from fastapi.staticfiles import StaticFiles
from ta.momentum import RSIIndicator, StochasticOscillator, WilliamsRIndicator
from ta.trend import MACD, EMAIndicator, ADXIndicator, CCIIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib

app = FastAPI()
app.mount("/static", StaticFiles(directory="frontend", html=True), name="frontend")

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backend")

# Criar um router para as rotas da API
api_router = APIRouter(prefix="/api")

executando = False
clients = set()
lock = threading.Lock()

historico_resultados = []
capital = 800.0
btc_posicao = 0.0
preco_entrada = 0.0
ultima_atualizacao_modelo = None

estado_atual = {
    "capital": capital,
    "btc_posicao": btc_posicao,
    "preco_entrada": preco_entrada,
    "sinal": "neutro",
    "timestamp": None,
    "historico_resultados": historico_resultados
}

@app.on_event("startup")
async def startup_event():
    for route in app.routes:
        if hasattr(route, "methods"):
            logger.info(f"Rota registrada: {route.path}, métodos: {route.methods}")

def adicionar_indicadores(df):
    df['rsi'] = RSIIndicator(close=df['close']).rsi()
    df['macd'] = MACD(close=df['close']).macd()
    df['ema_20'] = EMAIndicator(close=df['close'], window=20).ema_indicator()
    df['adx'] = ADXIndicator(high=df['high'], low=df['low'], close=df['close']).adx()
    df['obv'] = OnBalanceVolumeIndicator(close=df['close'], volume=df['volume']).on_balance_volume()
    df['bb_high'] = BollingerBands(close=df['close']).bollinger_hband()
    df['bb_low'] = BollingerBands(close=df['close']).bollinger_lband()
    df['atr'] = AverageTrueRange(high=df['high'], low=df['low'], close=df['close']).average_true_range()
    df['cci'] = CCIIndicator(high=df['high'], low=df['low'], close=df['close']).cci()
    df['stoch'] = StochasticOscillator(high=df['high'], low=df['low'], close=df['close']).stoch()
    df['williams_r'] = WilliamsRIndicator(high=df['high'], low=df['low'], close=df['close']).williams_r()
    return df.dropna()

# Inclua aqui suas outras funções: coletar_candles_binance, rotular_dados, treinar_modelo, restaurar_estado, ciclo_execucao, loop_ia, etc.

@api_router.post("/start")
async def start_execution(request: Request):
    global executando
    try:
        if executando:
            return {"status": "Já está executando"}
        executando = True
        threading.Thread(target=loop_ia, daemon=True).start()
        logger.info("Execução iniciada")
        return {"status": "Execução iniciada"}
    except Exception as e:
        logger.error(f"Erro no start_execution: {e}")
        return {"status": "Erro ao iniciar", "detalhes": str(e)}

@api_router.post("/stop")
async def stop_execution():
    global executando
    executando = False
    logger.info("Execução parada")
    return {"status": "Execução parada"}

@api_router.get("/status")
async def get_status():
    with lock:
        return estado_atual

@api_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    with lock:
        clients.add(websocket)
    try:
        while True:
            with lock:
                data = estado_atual.copy()
            await websocket.send_json(data)
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        with lock:
            clients.remove(websocket)

# Incluir o router na aplicação
app.include_router(api_router)
