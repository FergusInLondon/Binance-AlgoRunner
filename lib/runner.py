import pandas as pd

from account import Account
from binance.client import Client
from binance.websockets import BinanceSocketManager


class Runner(object):
    """
        The Runner is responsible for handling any exchange interactions,
        and running a given `Strategy` against the data that is provided
        from the exchange.

        A `Strategy` is expected to have two methods (a) `start()` - which
        performs any initialisation - such as configuring instance attributes,
        and (b) `process(runner, tick_dataframe)`, which computes any actions
        to run based upon the incoming data from the exchange.
    """

    def __init__(self, apiKey, apiSecret, symbol, runnable):
        self.client = Client(apiKey, apiSecret)

        account_info = self.client.get_account()
        self.account = Account(account_info)

        self.bm = BinanceSocketManager(self.client)
        self.bm.start_user_socket(self.account)

        self.symbol = symbol
        self.runnable = runnable

    def run(self):
        """
            Run is the main event loop, where data taken from the exchange
            is subsequently passed on to the underlying strategy.

            By passing this instance in to the strategy - via the `run(r, d)`
            method - it's possible for the strategy to invoke methods that
            interact with the exchange, via this runner; i.e to make buy/sell
            calls.
        """
        try:
            self.runnable.start(self)
        except AttributeError:
            print("invalid runnable: no 'start' method")
        self.bm.start_symbol_ticker_socket(
            self.symbol,
            lambda kline: self.runnable.process(self.parse_dataframe(kline)))
        self.bm.start()

    def parse_dataframe(self, kline):
        """
        """
        df = pd.DataFrame([kline])
        df.rename(columns=lambda col: {
                'e': "24hrTicker",
                'E': "EventTime",
                's': "Symbol",
                'p': "PriceChange",
                'P': "PriceChangePercent",
                'w': "WeightedAveragePrice",
                'x': "FirstTradePrice",
                'c': "LastPrice",
                'Q': "LastQuantity",
                'b': "BestBidPrice",
                'B': "BestBidQuantity",
                'a': "BestAskPrice",
                'A': "BestAskQuantity",
                'o': "OpenPrice",
                'h': "HighPrice",
                'l': "LowPrice",
                'v': "TotalTradedBaseAssetVolume",
                'q': "TotalTradedQuoteAssetVolume",
                'O': "StatisticsOpenTime",
                'C': "StatisticsCloseTime",
                'F': "FirstTradeId",
                'L': "LastTradeId",
                'n': "TotalNumberOfTrades",
            }[col],
            inplace=True)
        df.set_index('EventTime', inplace=True)
        df.index = pd.to_datetime(df.index, unit='ms')
        return df
