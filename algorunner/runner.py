from algorunner.trader import Trader
from algorunner.adapters import ADAPTERS, Credentials
from algorunner.exceptions import UnknownExchange
from algorunner.abstract.strategy import Strategy


class Runner(object):
    """
    The Runner is responsible for configuring all components required to execute
    a trading algorithm. It's called by the entrypoint of the app, located in
    `run.py`.
    """

    def __init__(self, creds: Credentials, symbol: str, strategy: Strategy):
        adapter_cls = ADAPTERS.get(creds["exchange"])
        if not adapter_cls:
            raise UnknownExchange(creds["exchange"])

        self.account = Trader()
        self.symbol = symbol
        self.strategy = strategy
        self.adapter = adapter_cls()

        self.adapter.connect(creds, self.account)

    def run(self):
        """ """
        self.adapter.run(self.strategy, self.symbol)
