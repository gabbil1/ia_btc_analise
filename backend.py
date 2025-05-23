import asyncio
import threading
import time
from datetime import datetime
import os
import json
import requests
import pandas as pd
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
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

# Monta frontend estático na raiz
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

# Estado global da execução
executando = False
clients = set()
lock = threading.Lock()

# Estado da IA
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

# ======= Funções IA e indicadores =======

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

def coletar_candles_binance(symbol="BTCUSDT", interval="1h", dias=365):
    url = "https://api.binance.com/api/v3/klines"
    limit = 1000
    interval_ms_map = {
        "1m": 60_000, "3m": 3*60_000, "5m": 5*60_000, "15m": 15*60_000,
        "30m": 30*60_000, "1h": 60*60_000, "2h": 2*60*60_000, "4h": 4*60*60_000,
        "6h": 6*60*60_000, "8h": 8*60*60_000, "12h": 12*60*60_000,
        "1d": 24*60*60_000, "3d": 3*24*60*60_000, "1w": 7*24*60*60_000,
        "1M": 30*24*60*60_000
    }
    interval_ms = interval_ms_map[interval]

    agora = int(time.time() * 1000)
    inicio = agora - dias * 24 * 60 * 60 * 1000

    todos_candles = []
    start_time = inicio

    while True:
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": start_time,
            "limit": limit
        }
        response = requests.get(url, params=params)
        data = response.json()

        if not data:
            break

        todos_candles.extend(data)

        ultimo_ts = data[-1][0]
        if ultimo_ts >= agora or len(data) < limit:
            break

        start_time = ultimo_ts + interval_ms
        time.sleep(0.1)

    df = pd.DataFrame(todos_candles, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
    ])

    df["open_time"] = pd.to_datetime(df["open_time"], unit='ms')
    df["close_time"] = pd.to_datetime(df["close_time"], unit='ms')
    numeric_cols = ["open", "high", "low", "close", "volume"]
    df[numeric_cols] = df[numeric_cols].astype(float)

    return df

def rotular_dados():
    df = pd.read_csv("historico_btc.csv")
    df['retorno_futuro'] = df['close'].shift(-3) / df['close'] - 1
    df['sinal'] = 'neutro'
    df.loc[df['retorno_futuro'] > 0.01, 'sinal'] = 'compra'
    df.loc[df['retorno_futuro'] < -0.01, 'sinal'] = 'venda'
    df = df.dropna()
    df.to_csv("dados_rotulados.csv", index=False)
    print(f"[✔] Dados rotulados ({len(df)} registros).")
    return df

def treinar_modelo():
    df = pd.read_csv("dados_rotulados.csv")
    X = df[['rsi', 'macd', 'ema_20', 'adx', 'obv', 'bb_high', 'bb_low', 'atr', 'cci', 'stoch', 'williams_r']]
    y = df['sinal']
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    X_train, _, y_train, _ = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
    modelo = GradientBoostingClassifier(n_estimators=200, learning_rate=0.1, max_depth=4)
    modelo.fit(X_train, y_train)
    joblib.dump(modelo, "modelo_ia_btc.pkl")
    joblib.dump(le, "rotulador_btc.pkl")
    print("[✔] Modelo treinado.")

def restaurar_estado():
    global capital, btc_posicao, preco_entrada
    try:
        df = pd.read_csv("historico_operacoes.csv")
        if df.empty:
            return
        ultima = df.iloc[-1]
        capital = ultima['capital']
        if ultima['acao'] == 'compra':
            btc_posicao = capital / ultima['preco'] if ultima['preco'] > 0 else 0
            preco_entrada = ultima['preco']
        print(f"[✔] Estado restaurado | Capital: {capital:.2f} | BTC: {btc_posicao:.6f} | Entrada: {preco_entrada:.2f}")
    except Exception as e:
        print(f"[ERRO] ao restaurar estado: {e}")

def ciclo_execucao():
    global capital, btc_posicao, preco_entrada, ultima_atualizacao_modelo, historico_resultados, estado_atual
    try:
        df = pd.read_csv("historico_btc.csv")
        df = adicionar_indicadores(df)
        modelo = joblib.load("modelo_ia_btc.pkl")
        le = joblib.load("rotulador_btc.pkl")
        ultima_linha = df.iloc[-1:]
        X = ultima_linha[['rsi', 'macd', 'ema_20', 'adx', 'obv', 'bb_high', 'bb_low', 'atr', 'cci', 'stoch', 'williams_r']]
        pred = modelo.predict(X)
        sinal = le.inverse_transform(pred)[0]
        timestamp = df.iloc[-1]['close_time']
        print(f"[1H] Sinal previsto: {sinal.upper()} | Timestamp: {timestamp}")

        preco_atual = df.iloc[-1]['close']
        if sinal == "compra" and capital > 0:
            btc_posicao = capital / preco_atual
            preco_entrada = preco_atual
            capital = 0
            historico_resultados.append({
                'timestamp': timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                'acao': 'compra',
                'preco': preco_atual,
                'capital': round(capital, 2)
            })

        elif sinal == "venda" and btc_posicao > 0:
            capital = btc_posicao * preco_atual
            lucro = capital - (btc_posicao * preco_entrada)
            historico_resultados.append({
                'timestamp': timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                'acao': 'venda',
                'preco': preco_atual,
                'lucro': round(lucro, 2),
                'capital': round(capital, 2)
            })
            btc_posicao = 0
            preco_entrada = 0

        if historico_resultados:
            pd.DataFrame(historico_resultados).to_csv("historico_operacoes.csv", index=False)

        with lock:
            estado_atual.update({
                "capital": capital,
                "btc_posicao": btc_posicao,
                "preco_entrada": preco_entrada,
                "sinal": sinal,
                "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "historico_resultados": historico_resultados[-10:]  # últimos 10 registros
            })

        agora = datetime.now()
        if ultima_atualizacao_modelo is None or (agora - ultima_atualizacao_modelo).total_seconds() > 86400:
            rotular_dados()
            treinar_modelo()
            ultima_atualizacao_modelo = agora

    except Exception as e:
        print(f"Erro durante execução: {e}")

# ======= Loop de execução controlado =======

def loop_ia():
    global executando
    restaurar_estado()
    while executando:
        ciclo_execucao()
        time.sleep(300)  # 5 minutos

async def send_json_safe(ws, data):
    try:
        await ws.send_json(data)
    except:
        pass

@app.post("/start")
async def start_execution():
    global executando
    if executando:
        return {"status": "Já está executando"}
    executando = True
    threading.Thread(target=loop_ia, daemon=True).start()
    return {"status": "Execução iniciada"}

@app.post("/stop")
async def stop_execution():
    global executando
    executando = False
    return {"status": "Execução parada"}

@app.get("/status")
async def get_status():
    with lock:
        return estado_atual

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)
    try:
        while True:
            await websocket.receive_text()  # mantém conexão viva
            # Enviar estado atual a cada mensagem recebida
            with lock:
                await websocket.send_json(estado_atual)
    except WebSocketDisconnect:
        clients.remove(websocket)
