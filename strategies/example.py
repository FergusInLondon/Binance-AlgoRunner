import pandas as pd

from algorunner.adapters import TransactionRequest
from algorunner.mutations import AccountState
from algorunner.strategy import BaseStrategy


class Example(BaseStrategy):
    """
    A simple example strategy that computes the average price change over
    the previous 5 2000ms updates.
    """

    # this tag is used in a unit test targeting the strategy loader. ignore!
    _testing_tag = True

    def __init__(self):
        self.series = pd.DataFrame
        super().__init__()

    def process(self, tick):
        self.series = self.series.append(tick)

        if self.series.shape[0] > 5:
            recent_window = pd.to_numeric(self.series[-5:]["PriceChange"])
            print("Average price change over past 5 windows: ", recent_window.mean())

    def authorise(self, state: AccountState, trx: TransactionRequest) -> TransactionRequest:
        pass
