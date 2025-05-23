# === IMPORTS INICIAIS ===
import ccxt
import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator, StochasticOscillator, WilliamsRIndicator
from ta.trend import MACD, EMAIndicator, ADXIndicator, CCIIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
import time
import os
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib
import matplotlib.pyplot as plt

# === CONTROLE DE CAPITAL E POSIÇÃO ===
historico_resultados = []
capital = 800.0
btc_posicao = 0.0
preco_entrada = 0.0
ultima_atualizacao_modelo = None

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

# === ADICIONAR INDICADORES ===
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

# === COLETA HISTÓRICA ===
def coletar_historico(par='BTC/USDT', timeframe='1h', dias=365, arquivo='historico_btc.csv'):
    print(f"[COLETA HISTÓRICA] Baixando {dias} dias ({timeframe}) do par {par}...")
    exchange = ccxt.binance()
    limite = 1000
    ms_por_candle = exchange.parse_timeframe(timeframe) * 1000
    agora = exchange.milliseconds()
    desde = agora - (dias * 24 * 60 * 60 * 1000)
    todos_candles = []
    while desde < agora:
        candles = exchange.fetch_ohlcv(par, timeframe=timeframe, since=desde, limit=limite)
        if not candles:
            break
        todos_candles += candles
        desde = candles[-1][0] + ms_por_candle
        time.sleep(0.1)
    df = pd.DataFrame(todos_candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True).dt.tz_convert("America/Sao_Paulo")
    df = adicionar_indicadores(df)
    df.to_csv(arquivo, index=False)
    print(f"[✔] Histórico salvo em {arquivo} ({len(df)} registros).")

# === RÓTULOS E TREINAMENTO ===
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

# === EXECUÇÃO ===
def ciclo_execucao():
    global capital, btc_posicao, preco_entrada, ultima_atualizacao_modelo
    try:
        df = pd.read_csv("historico_btc.csv")
        df = adicionar_indicadores(df)
        modelo = joblib.load("modelo_ia_btc.pkl")
        le = joblib.load("rotulador_btc.pkl")
        ultima_linha = df.iloc[-1:]
        X = ultima_linha[['rsi', 'macd', 'ema_20', 'adx', 'obv', 'bb_high', 'bb_low', 'atr', 'cci', 'stoch', 'williams_r']]
        pred = modelo.predict(X)
        sinal = le.inverse_transform(pred)[0]
        timestamp = df.iloc[-1]['timestamp']
        print(f"[1H] Sinal previsto: {sinal.upper()} | Timestamp: {timestamp}")

        preco_atual = df.iloc[-1]['close']
        if sinal == "compra" and capital > 0:
            btc_posicao = capital / preco_atual
            preco_entrada = preco_atual
            capital = 0
            historico_resultados.append({
                'timestamp': timestamp,
                'acao': 'compra',
                'preco': preco_atual,
                'capital': round(capital, 2)
            })

        elif sinal == "venda" and btc_posicao > 0:
            capital = btc_posicao * preco_atual
            lucro = capital - (btc_posicao * preco_entrada)
            historico_resultados.append({
                'timestamp': timestamp,
                'acao': 'venda',
                'preco': preco_atual,
                'lucro': round(lucro, 2),
                'capital': round(capital, 2)
            })
            btc_posicao = 0
            preco_entrada = 0

        if historico_resultados:
            pd.DataFrame(historico_resultados).to_csv("historico_operacoes.csv", index=False)

        agora = datetime.now()
        if ultima_atualizacao_modelo is None or (agora - ultima_atualizacao_modelo).total_seconds() > 86400:
            rotular_dados()
            treinar_modelo()
            ultima_atualizacao_modelo = agora

    except Exception as e:
        print(f"Erro durante execução: {e}")

# === INICIALIZAÇÃO ===
if __name__ == "__main__":
    if not os.path.exists("modelo_ia_btc.pkl") or not os.path.exists("rotulador_btc.pkl"):
        coletar_historico()
        rotular_dados()
        treinar_modelo()
    restaurar_estado()
    while True:
        ciclo_execucao()
        time.sleep(300)  # 5 minutos

