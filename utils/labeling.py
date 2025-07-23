import pandas as pd

def rotular_dados(df, tipo='classificacao', janela=1, limiar=0.002):
    '''
    tipo: 'classificacao' ou 'regressao'
    janela: quantos períodos à frente olhar
    limiar: variação percentual para definir compra/venda
    '''
    df = df.copy()
    df['retorno_futuro'] = df['close'].shift(-janela) / df['close'] - 1
    if tipo == 'classificacao':
        # Compra: retorno futuro > limiar; Venda: < -limiar; Neutro: entre
        df['sinal'] = 'neutro'
        df.loc[df['retorno_futuro'] > limiar, 'sinal'] = 'compra'
        df.loc[df['retorno_futuro'] < -limiar, 'sinal'] = 'venda'
        return df.dropna(subset=['retorno_futuro'])
    elif tipo == 'regressao':
        df['preco_futuro'] = df['close'].shift(-janela)
        return df.dropna(subset=['preco_futuro'])
    else:
        raise ValueError('tipo deve ser "classificacao" ou "regressao"') 