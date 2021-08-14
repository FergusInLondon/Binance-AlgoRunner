from csv import reader
from threading import Thread
from typing import Callable, List

from algorunner.adapters.base import Adapter, register_adapter
from algorunner.adapters.messages import (
    Credentials,
    TransactionRequest,
)


def transform_csv(row: List[str]) -> any:
    pass


@register_adapter
class BacktestAdapter(Adapter):

    identifier = "backtest"

    def connect(self, creds: Credentials):
        # We abuse the Credentials object here: and use the given parameters
        # to determine filenames.
        self.datafile = creds.exchange
        self.outfile = creds.key

    def monitor_user(self):
        # We wont provide user updates in backtest mode. This may be cause
        # some functionality problems though (i.e. when `authorise()` relies
        # upon account status).
        pass

    def run(self, symbol: str, process: Callable):
        #
        #
        #
        def process_file():
            with open(self.datafile, "r") as csv:
                for row in reader(csv):
                    process(transform_csv(row))

        self.thread = Thread(target=process_file, daemon=True)
        self.thread.start()

    def execute(self, trx: TransactionRequest) -> bool:
        pass

    def disconnect(self):
        if self.thread.is_alive():
            self.thread.join()
