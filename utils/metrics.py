from sklearn.metrics import mean_squared_error, mean_absolute_error, accuracy_score
import numpy as np

def calcular_metricas_regressao(y_true, y_pred):
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_true, y_pred)
    return {'MSE': mse, 'RMSE': rmse, 'MAE': mae}

def calcular_metricas_classificacao(y_true, y_pred):
    acc = accuracy_score(y_true, y_pred)
    return {'Acuracia': acc} 