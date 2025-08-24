import numpy as np
import pandas as pd

class Backtester:
    def __init__(self, price: pd.Series, cash: float = 100000, commission: float = 0.0):
        self.price = price
        self.dates = price.index
        self.cash = cash
        self.init_cash = cash
        self.position = 0.0
        self.position_price = 0.0
        self.commission = commission
        self.history = []

    def run_signals(self, signals: pd.Series, pct_risk: float = 0.1):
        """signals aligned with price index. pct_risk controls max notional per trade."""
        signals = signals.reindex(self.dates).fillna(0).astype(float)
        equity_series = []
        cash = self.cash
        position = 0.0
        position_price = 0.0
        for t in self.dates:
            s = signals.loc[t]
            p = self.price.loc[t]
            # Exit condition
            if position != 0 and s == 0:
                # close
                cash += position * p
                cash -= abs(position) * self.commission
                self.history.append((t, 'exit', position, p, cash))
                position = 0
                position_price = 0
            # Entry
            if position == 0 and s != 0:
                notional = self.init_cash * pct_risk
                size = (notional / p) * s # signed
                position = size
                position_price = p
                cash -= size * p
                cash -= abs(size) * self.commission
                self.history.append((t, 'enter', position, p, cash))
            # mark-to-market
            equity = cash + position * p
            equity_series.append((t, equity))
        eq = pd.Series([v for _, v in equity_series], index=[d for d, _ in equity_series])
        return eq

    @staticmethod
    def performance_metrics(equity: pd.Series):
        returns = equity.pct_change().fillna(0)
        total_return = equity.iloc[-1] / equity.iloc[0] - 1.0
        ann_ret = (1 + total_return) ** (252 / len(equity)) - 1 if len(equity) > 1 else 0.0
        ann_vol = returns.std() * np.sqrt(252)
        sharpe = ann_ret / ann_vol if ann_vol != 0 else np.nan
        # max drawdown
        running_max = equity.cummax()
        drawdown = (equity - running_max) / running_max
        max_dd = drawdown.min()
        return {
            'total_return': float(total_return),
            'ann_return': float(ann_ret),
            'ann_vol': float(ann_vol),
            'sharpe': float(sharpe),
            'max_drawdown': float(max_dd)
        }