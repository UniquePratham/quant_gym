import pandas as pd

def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    
    # Use exponential moving average for smoother RSI
    up_ema = up.ewm(span=period, adjust=False).mean()
    down_ema = down.ewm(span=period, adjust=False).mean()
    
    rs = up_ema / down_ema
    rsi = 100 - (100 / (1 + rs))
    return rsi

def generate_signals(price: pd.Series, low: int = 30, high: int = 70, period: int = 14) -> pd.Series:
    df = pd.DataFrame({'close': price})
    df['rsi'] = rsi(df['close'], period)
    
    # Generate signals based on RSI levels
    df['signal'] = 0
    # Buy when RSI crosses above oversold level
    df.loc[(df['rsi'] > low) & (df['rsi'].shift(1) <= low), 'signal'] = 1
    # Sell when RSI crosses below overbought level
    df.loc[(df['rsi'] < high) & (df['rsi'].shift(1) >= high), 'signal'] = -1
    # Exit when RSI crosses back to neutral
    df.loc[((df['rsi'] < low) & (df['rsi'].shift(1) >= low)) | 
           ((df['rsi'] > high) & (df['rsi'].shift(1) <= high)), 'signal'] = 0
    
    # Convert signal changes to positions
    current_position = 0
    positions = []
    
    for signal in df['signal']:
        if signal != 0:  # Only change position on actual signals
            current_position = signal
        positions.append(current_position)
    
    return pd.Series(positions, index=df.index, name='position')