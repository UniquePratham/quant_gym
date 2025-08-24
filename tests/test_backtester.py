import pandas as pd
from backtester import Backtester


def test_backtester_basic():
dates = pd.date_range('2020-01-01', periods=10)
price = pd.Series([100 + i for i in range(10)], index=dates)
# simple buy at start hold till end
signals