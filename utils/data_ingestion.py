import requests
import pandas as pd

def coletar_candles_binance(symbol="BTCUSDT", interval="1d", limit=1000):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data, columns=[
        'open_time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    df['open'] = df['open'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    df['close'] = df['close'].astype(float)
    df['volume'] = df['volume'].astype(float)
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    return df[['open_time', 'open', 'high', 'low', 'close', 'volume']]

def coletar_hashrate_coingecko():
    # CoinGecko não fornece hashrate diário diretamente, mas CoinWarz/CoinMetrics fornecem
    # Exemplo CoinWarz (gratuito, sem API key):
    url = "https://www.coinwarz.com/v1/api/bitcoin/network/hashrate"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        # Hashrate em PH/s
        hashrate = data['Data']['Hashrate']
        return hashrate
    except Exception as e:
        print(f"Erro ao coletar hashrate: {e}")
        return None 