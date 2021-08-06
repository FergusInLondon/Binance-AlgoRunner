from queue import Queue

from algorunner import abstract
from algorunner.adapters import ADAPTERS, Credentials
from algorunner.exceptions import UnknownExchange
from algorunner.trader import Trader


class Runner(object):
    """
    The Runner is responsible for configuring all components required to execute
    a trading algorithm. It's called by the entrypoint of the app, located in
    `run.py`.
    """

    def __init__(self,
                 creds: Credentials,
                 symbol: str,
                 strategy: abstract.Strategy,
                 calculator: abstract.Calculator):
        adapter_cls = ADAPTERS.get(creds["exchange"])
        if not adapter_cls:
            raise UnknownExchange(creds["exchange"])

        self.adapter = adapter_cls()
        self.strategy = strategy
        self.symbol = symbol

        trade_queue = Queue()
        self.trader = Trader(
            symbol=symbol,
            queue=trade_queue,
            adapter=self.adapter,
            calculator=calculator
        )

        self.adapter.connect(creds, self.trader)

    def run(self):
        """ """
        self.adapter.run(self.strategy, self.symbol)

    def stop(self):
        # @todo - for graceful shutdown
        pass
