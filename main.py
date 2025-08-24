import pandas as pd
import numpy as np
from backtester import Backtester
import utils
from strategies import sma_crossover, rsi_meanrev, market_mood

def run_single_asset_strategy(symbol: str, gen_signals_fn, start='2020-01-01'):
    df = utils.download_data(symbol, start=start)
    
    # Debug: print column names to verify
    print(f"Columns for {symbol}: {df.columns.tolist()}")
    
    # Use 'close' instead of 'adj_close' since that's what yfinance now returns
    price = df['close']
    signals = gen_signals_fn(price)
    bt = Backtester(price, cash=100000, commission=0.0)
    equity = bt.run_signals(signals)
    metrics = Backtester.performance_metrics(equity)
    print(f"\n=== {gen_signals_fn.__name__} on {symbol} ===")
    for k, v in metrics.items():
        print(f"{k}: {v}")
    utils.plot_equity(equity, f"{gen_signals_fn.__name__}_{symbol}")
    return equity, metrics

def run_market_mood(start='2020-01-01'):
    # pair: BTC-USD vs QQQ
    a = utils.download_data('BTC-USD', start=start)
    b = utils.download_data('QQQ', start=start)
    
    # Debug: print column names to verify
    print(f"Columns for BTC-USD: {a.columns.tolist()}")
    print(f"Columns for QQQ: {b.columns.tolist()}")
    
    # Use 'close' instead of 'adj_close' since that's what yfinance now returns
    price_a = a['close']
    price_b = b['close']
    dfpos = market_mood.generate_pairs_signals(price_a, price_b)
    # create synthetic combined equity: assume $100k initial, split into two legs of 50k each
    init = 100000
    notional = init / 2
    # compute each leg equity
    eq_a = (notional * (price_a.reindex(dfpos.index) / price_a.reindex(dfpos.index).iloc[0]) * (dfpos['pos_a'].replace(0, np.nan).ffill().fillna(0)))
    eq_b = (notional * (price_b.reindex(dfpos.index) / price_b.reindex(dfpos.index).iloc[0]) * (dfpos['pos_b'].replace(0, np.nan).ffill().fillna(0)))
    # combined equity (cash + mark-to-market). For simplicity, treat positions as fully invested when pos !=0
    combined = eq_a.fillna(0) + eq_b.fillna(0) + (init - notional*(dfpos['pos_a'].abs().iloc[0] + dfpos['pos_b'].abs().iloc[0]))
    combined.index = dfpos.index
    utils.plot_equity(combined, 'market_mood_combined')
    metrics = Backtester.performance_metrics(combined)
    print("\n=== Market Mood Detector (BTC vs QQQ) ===")
    for k, v in metrics.items():
        print(f"{k}: {v}")
    return combined, metrics

if __name__ == '__main__':
    # Run baselines
    eq1, m1 = run_single_asset_strategy('QQQ', sma_crossover.generate_signals)
    eq2, m2 = run_single_asset_strategy('QQQ', rsi_meanrev.generate_signals)
    eq3, m3 = run_market_mood()
    utils.compare_results({'SMA_QQQ': eq1, 'RSI_QQQ': eq2, 'MarketMood': eq3})
    print('\nAll done. Plots saved to outputs/')