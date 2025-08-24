import pandas as pd

def generate_signals(price: pd.Series, short_window: int = 20, long_window: int = 50) -> pd.Series:
    df = pd.DataFrame({'close': price})
    df['sma_s'] = df['close'].rolling(short_window).mean()
    df['sma_l'] = df['close'].rolling(long_window).mean()
    
    # Generate signals based on crossover
    df['signal'] = 0
    # Golden cross: short MA crosses above long MA -> BUY
    df.loc[(df['sma_s'] > df['sma_l']) & (df['sma_s'].shift(1) <= df['sma_l'].shift(1)), 'signal'] = 1
    # Death cross: short MA crosses below long MA -> SELL
    df.loc[(df['sma_s'] < df['sma_l']) & (df['sma_s'].shift(1) >= df['sma_l'].shift(1)), 'signal'] = -1
    
    # Convert signal changes to positions (hold until opposite signal)
    current_position = 0
    positions = []
    
    for signal in df['signal']:
        if signal != 0:  # Only change position on actual crossover signals
            current_position = signal
        positions.append(current_position)
    
    return pd.Series(positions, index=df.index, name='position')