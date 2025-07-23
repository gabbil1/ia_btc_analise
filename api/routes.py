from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request
import threading
import asyncio
import logging
from model.core import loop_ia
import joblib
import numpy as np
from utils.data_ingestion import coletar_candles_binance
from utils.indicators import adicionar_indicadores
from sklearn.preprocessing import LabelEncoder

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

logger = logging.getLogger("backend")

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

@api_router.post("/train")
async def train_model(request: Request):
    body = await request.json()
    modelo = body.get('modelo', 'randomforest')
    tipo = body.get('tipo', 'classificacao')
    janela = body.get('janela', 1)
    limiar = body.get('limiar', 0.002)
    from model.core import loop_ia
    metricas = loop_ia(modelo=modelo, tipo=tipo, janela=janela, limiar=limiar)
    return {"status": "treinamento finalizado", "metricas": metricas}

@api_router.post("/predict")
async def predict(request: Request):
    body = await request.json()
    modelo = body.get('modelo', 'randomforest')
    tipo = body.get('tipo', 'classificacao')
    # Carregar modelo treinado
    model_path = f'data/modelo_{modelo}_{tipo}.pkl'
    try:
        model = joblib.load(model_path)
    except Exception as e:
        return {"status": "erro", "detalhes": f"Modelo não encontrado: {e}"}
    # Coletar último candle
    df = coletar_candles_binance(limit=2)
    df = adicionar_indicadores(df)
    features = [c for c in df.columns if c not in ['open_time','sinal','preco_futuro','retorno_futuro']]
    X = df.iloc[[-1]][features].values
    # Prever
    if tipo == 'classificacao':
        y_pred = model.predict(X)
        # Decodificar se necessário
        labels = ['compra','neutro','venda']
        try:
            le = LabelEncoder()
            le.fit(labels)
            pred_label = le.inverse_transform(y_pred)[0]
        except:
            pred_label = str(y_pred[0])
        return {"status": "ok", "previsao": pred_label}
    else:
        y_pred = model.predict(X)
        return {"status": "ok", "previsao": float(y_pred[0])}

@api_router.post("/update_data")
async def update_data(request: Request = None):
    from utils.data_ingestion import coletar_candles_binance
    import os
    import pandas as pd
    df = coletar_candles_binance()
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/btc_data.csv', index=False)
    return {"status": "ok", "registros": len(df), "arquivo": "data/btc_data.csv"}

@api_router.get("/model_info")
async def model_info():
    import os
    import json
    info_path = 'data/model_info.json'
    if not os.path.exists(info_path):
        return {"status": "erro", "detalhes": "Nenhum modelo treinado ainda."}
    with open(info_path, 'r') as f:
        info = json.load(f)
    return {"status": "ok", "info": info} 