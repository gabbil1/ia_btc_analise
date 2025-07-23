from utils.data_ingestion import coletar_candles_binance, coletar_hashrate_coingecko
from utils.indicators import adicionar_indicadores
from utils.labeling import rotular_dados
from utils.metrics import calcular_metricas_regressao, calcular_metricas_classificacao
from utils.sentiment import sentimento_bitcoin
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from xgboost import XGBRegressor, XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib
import numpy as np
import json
from datetime import datetime

# LSTM opcional
try:
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense
    HAS_TF = True
except ImportError:
    HAS_TF = False

def loop_ia(modelo='randomforest', tipo='classificacao', janela=1, limiar=0.002):
    # 1. Coletar dados
    df = coletar_candles_binance()
    # 2. Adicionar indicadores técnicos
    df = adicionar_indicadores(df)
    # 3. Adicionar hashrate e outras features (placeholder)
    hashrate = coletar_hashrate_coingecko()
    if hashrate is not None:
        df['hashrate'] = hashrate
    else:
        df['hashrate'] = 0
    sentimento = sentimento_bitcoin()
    df['sentimento'] = sentimento
    # 4. Rotular dados
    df = rotular_dados(df, tipo=tipo, janela=janela, limiar=limiar)
    # 5. Preparar X e y
    features = [c for c in df.columns if c not in ['open_time','sinal','preco_futuro','retorno_futuro']]
    X = df[features].values
    if tipo == 'classificacao':
        y = df['sinal'].values
        le = LabelEncoder()
        y = le.fit_transform(y)
    else:
        y = df['preco_futuro'].values
    # 6. Split train/test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
    # 7. Treinar modelo
    if modelo == 'randomforest':
        if tipo == 'classificacao':
            model = RandomForestClassifier()
        else:
            model = RandomForestRegressor()
    elif modelo == 'xgboost':
        if tipo == 'classificacao':
            model = XGBClassifier()
        else:
            model = XGBRegressor()
    elif modelo == 'lstm' and HAS_TF:
        # LSTM requer reshape e normalização
        X_train_lstm = X_train.reshape((X_train.shape[0], 1, X_train.shape[1]))
        X_test_lstm = X_test.reshape((X_test.shape[0], 1, X_test.shape[1]))
        model = Sequential()
        model.add(LSTM(50, input_shape=(1, X_train.shape[1])))
        model.add(Dense(1 if tipo=='regressao' else len(np.unique(y_train)), activation='softmax' if tipo=='classificacao' else 'linear'))
        model.compile(loss='mse' if tipo=='regressao' else 'sparse_categorical_crossentropy', optimizer='adam')
        model.fit(X_train_lstm, y_train, epochs=10, batch_size=32, verbose=0)
        y_pred = model.predict(X_test_lstm)
        if tipo == 'classificacao':
            y_pred = np.argmax(y_pred, axis=1)
    else:
        raise ValueError('Modelo não suportado ou TensorFlow não instalado')
    if modelo != 'lstm':
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
    # 8. Métricas
    if tipo == 'classificacao':
        metricas = calcular_metricas_classificacao(y_test, y_pred)
    else:
        metricas = calcular_metricas_regressao(y_test, y_pred)
    # 9. Salvar modelo
    if modelo != 'lstm':
        joblib.dump(model, f'data/modelo_{modelo}_{tipo}.pkl')
    # Salvar metadados
    info = {
        'modelo': modelo,
        'tipo': tipo,
        'data_treino': datetime.now().isoformat(),
        'metricas': metricas
    }
    with open('data/model_info.json', 'w') as f:
        json.dump(info, f, indent=2)
    # 10. Retornar métricas
    print('Métricas:', metricas)
    return metricas 