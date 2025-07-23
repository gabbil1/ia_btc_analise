from ta.momentum import RSIIndicator, StochasticOscillator, WilliamsRIndicator
from ta.trend import MACD, EMAIndicator, ADXIndicator, CCIIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator

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