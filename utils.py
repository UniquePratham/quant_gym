# utils.py
import os
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np

os.makedirs('outputs', exist_ok=True)

def download_data(symbol, start="2015-01-01", end="2025-01-01"):
    df = yf.download(symbol, start=start, end=end, progress=False)
    
    # SIMPLIFIED: Always use the first level of MultiIndex and rename
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    # Standardize column names
    column_mapping = {
        "Adj Close": "close",
        "Close": "close", 
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Volume": "volume"
    }
    
    df = df.rename(columns=column_mapping)
    
    # Ensure we have close price
    if 'close' not in df.columns and len(df.columns) > 0:
        df['close'] = df.iloc[:, 0]  # Use first column as close price
    
    return df

def download_symbol(symbol, start="2015-01-01", end="2025-01-01"):
    return download_data(symbol, start, end)

def save_plot(fig, name: str):
    path = f'outputs/{name}'
    fig.savefig(path, bbox_inches='tight', dpi=300)
    plt.close(fig)

def plot_equity(equity: pd.Series, title: str):
    fig, ax = plt.subplots(figsize=(12, 6))
    equity.plot(ax=ax, linewidth=2)
    ax.set_title(f'Equity Curve: {title}', fontsize=14, fontweight='bold')
    ax.set_ylabel('Equity ($)', fontsize=12)
    ax.set_xlabel('Date', fontsize=12)
    ax.grid(True, alpha=0.3)
    save_plot(fig, f'equity_{title.replace(" ","_").lower()}.png')

def compare_results(res_dict: dict):
    fig, ax = plt.subplots(figsize=(12, 7))
    for k, v in res_dict.items():
        normalized = v / v.iloc[0]  # Normalize to starting value
        normalized.plot(ax=ax, label=k, linewidth=2)
    
    ax.legend(fontsize=12)
    ax.set_title('Equity Curve Comparison (Normalized)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Normalized Equity', fontsize=12)
    ax.set_xlabel('Date', fontsize=12)
    ax.grid(True, alpha=0.3)
    save_plot(fig, 'equity_comparison.png')

def calculate_performance_metrics(equity_curve):
    """Calculate comprehensive performance metrics"""
    returns = equity_curve.pct_change().fillna(0)
    
    metrics = {
        'total_return': (equity_curve.iloc[-1] / equity_curve.iloc[0]) - 1,
        'annual_return': (1 + (equity_curve.iloc[-1] / equity_curve.iloc[0]) - 1) ** (252/len(equity_curve)) - 1,
        'annual_volatility': returns.std() * np.sqrt(252),
        'sharpe_ratio': (returns.mean() * 252) / (returns.std() * np.sqrt(252)) if returns.std() > 0 else 0,
        'max_drawdown': (equity_curve / equity_curve.cummax() - 1).min(),
        'calmar_ratio': abs((returns.mean() * 252) / ((equity_curve / equity_curve.cummax() - 1).min())) if ((equity_curve / equity_curve.cummax() - 1).min()) < 0 else 0
    }
    
    return metrics