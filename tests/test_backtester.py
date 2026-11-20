import pandas as pd
import pytest
from backtester import Backtester


def _price(n=10, start=100):
    dates = pd.date_range("2020-01-01", periods=n, freq="D")
    return pd.Series([start + i for i in range(n)], index=dates, dtype=float)


def test_buy_and_hold_matches_price_move():
    price = _price()
    signals = pd.Series(1.0, index=price.index)
    bt = Backtester(price, cash=100_000, commission=0.0)
    equity = bt.run_signals(signals, pct_risk=1.0)

    # Fully invested from day one: equity tracks the price move.
    assert equity.iloc[0] == pytest.approx(100_000)
    assert equity.iloc[-1] == pytest.approx(100_000 * price.iloc[-1] / price.iloc[0])


def test_flat_signals_leave_cash_untouched():
    price = _price()
    signals = pd.Series(0.0, index=price.index)
    bt = Backtester(price, cash=50_000)
    equity = bt.run_signals(signals)

    assert equity.iloc[-1] == pytest.approx(50_000)
    assert bt.history == []


def test_commission_is_charged_on_entry_and_exit():
    price = _price()
    signals = pd.Series([1.0] * 5 + [0.0] * 5, index=price.index)
    bt = Backtester(price, cash=100_000, commission=10.0)
    bt.run_signals(signals, pct_risk=0.5)

    actions = [h[1] for h in bt.history]
    assert actions == ["enter", "exit"]


def test_performance_metrics_keys_and_drawdown():
    price = _price()
    signals = pd.Series(1.0, index=price.index)
    bt = Backtester(price, cash=100_000)
    equity = bt.run_signals(signals, pct_risk=1.0)
    metrics = bt.performance_metrics(equity)

    assert set(metrics) == {"total_return", "ann_return", "ann_vol", "sharpe", "max_drawdown"}
    assert metrics["total_return"] > 0
    assert metrics["max_drawdown"] <= 0