import pandas as pd

from algorunner.adapters import TransactionRequest
from algorunner.hooks import Hook
from algorunner.mutations import AccountState
from algorunner.strategy import BaseStrategy

from logging import getLogger


class Example(BaseStrategy):
    """
    A simple example strategy that computes the average price change over
    the previous 5 2000ms updates.
    """

    # this tag is used in a unit test targeting the strategy loader. ignore!
    _testing_tag = True

    def __init__(self):
        super().__init__()
        self.series = pd.DataFrame
        self.logger = getLogger()
        self.register_hooks({
            Hook.API_EXECUTE_DURATION: self.handle_api_duration,
            Hook.PROCESS_DURATION: self.handle_process_duration,
        })

    def process(self, tick):
        self.series = self.series.append(tick)

        if self.series.shape[0] > 5:
            recent_window = pd.to_numeric(self.series[-5:]["PriceChange"])
            self.logger.info("Average price change over past 5 windows: ", recent_window.mean())

    def authorise(self, state: AccountState, trx: TransactionRequest) -> TransactionRequest:
        pass

    # AlgoRunner additionally provides hooks for monitoring execution
    # performance and being able to respond to internal events.
    # @see BaseStrategy.register_hooks
    def handle_api_duration(self, duration: float):
        self.logger.info(f"api call duration: {duration}ms")

    def handle_process_duration(self, duration: float):
        self.logger.info(f"tick process duration: {duration}ms")
