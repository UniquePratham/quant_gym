# strategies/market_mood.py
import pandas as pd
import numpy as np

def generate_pairs_signals(price_a, price_b, window=20, entry_z=2.0, exit_z=0.5):
    """
    Generate pairs trading signals based on z-score of spread between two assets.
    """
    # Align the two price series
    df = pd.DataFrame({'a': price_a, 'b': price_b}).dropna()
    
    # Calculate spread (price_a - price_b)
    df['spread'] = df['a'] - df['b']
    
    # Calculate z-score of spread
    rolling_mean = df['spread'].rolling(window=window).mean()
    rolling_std = df['spread'].rolling(window=window).std()
    
    # Avoid division by zero
    rolling_std = rolling_std.replace(0, 1)
    
    df['z'] = (df['spread'] - rolling_mean) / rolling_std
    
    # Generate SIGNAL changes (not positions)
    df['signal_change'] = 0
    df.loc[(df['z'] > entry_z) & (df['z'].shift(1) <= entry_z), 'signal_change'] = -1  # Enter short spread
    df.loc[(df['z'] < -entry_z) & (df['z'].shift(1) >= -entry_z), 'signal_change'] = 1   # Enter long spread
    df.loc[(abs(df['z']) < exit_z) & (abs(df['z'].shift(1)) >= exit_z), 'signal_change'] = 0  # Exit position
    
    # Convert signal changes to positions (hold until exit signal)
    current_signal = 0
    positions = []
    
    for change in df['signal_change']:
        if change != 0:
            current_signal = change
        positions.append(current_signal)
    
    df['position'] = positions
    
    # Create position dataframe
    dfpos = pd.DataFrame(index=df.index)
    dfpos['pos_a'] = df['position']  # Position in asset A
    dfpos['pos_b'] = -df['position']  # Position in asset B (inverse)
    
    return dfpos