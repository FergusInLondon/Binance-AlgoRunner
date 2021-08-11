import pandas as pd
from logging import Logger

from algorunner.abstract import BaseStrategy
from algorunner.abstract.base_strategy import (
    AccountState, TransactionRequest, AuthorisationDecision
)


class Example(BaseStrategy):
    """
    A simple example strategy that computes the average price change over
    the previous 5 2000ms updates.
    """

    # this tag is used in a unit test targeting the strategy loader. ignore!
    _testing_tag = True

    def __init__(self, log: Logger):
        self.series = pd.DataFrame
        super().__init__(log)

    def process(self, tick):
        self.series = self.series.append(tick)

        if self.series.shape[0] > 5:
            recent_window = pd.to_numeric(self.series[-5:]["PriceChange"])
            print("Average price change over past 5 windows: ", recent_window.mean())

    def authorise(self, state: AccountState, trx: TransactionRequest) -> AuthorisationDecision:
        pass
