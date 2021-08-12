from typing import Callable

from binance.client import Client
from binance import BinanceSocketManager

import pandas as pd

from algorunner.adapters.base import (
    Adapter, Credentials, InvalidPayloadRecieved
)

from algorunner.mutations import (
    AccountUpdate, BaseUpdate, BalanceUpdate, CapabilitiesUpdate, Position
)


class BinanceAdapter(Adapter):
    """ """

    class MarketStreamRawTransformer:
        pass

    class MarketStreamPandasTransformer:
        def __call__(self, tick) -> pd.DataFrame:
            """Converts the inbound tick to something exchange-agnostic."""
            df = pd.DataFrame([tick])
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

    class UserStreamEventTransformer:
        """ """

        def __call__(self, payload) -> BaseUpdate:
            try:
                message_map = {
                    "outboundAccountInfo": self.account_update,
                    "outboundAccountPosition": self.position_update,
                    "balanceUpdate": self.balance_update,
                    "executionReport": self.order_report
                }

                # what if we need to return multiple? i.e CapabilitiesUpdate AND AccountUpdate
                return message_map[payload["e"]](payload)
            except KeyError:
                msg = "unknown payload type {p}".format(p=payload.get("e"))
                raise InvalidPayloadRecieved(msg)
            except Exception as e:
                raise Exception("unknown error occured in user stream", e)

        def initial_rest_payload(self, payload) -> CapabilitiesUpdate:
            # @todo - there is so much data in this payload that we're missing
            # out on, like commission rates etc.
            return CapabilitiesUpdate(
                can_withdraw=payload["canWithdraw"],
                can_trade=payload["canTrade"],
                can_deposit=payload["canDeposit"],
                positions=[Position(
                    asset=b["asset"], free=b["free"], locked=b["locked"]
                ) for b in payload["balances"]]
            )

        def account_update(self, payload) -> AccountUpdate:
            return AccountUpdate(balances=[Position(
                asset=b["asset"], free=b["free"], locked=b["locked"]
                ) for b in payload["B"]
            ])

        def balance_update(self, payload) -> BalanceUpdate:
            return BalanceUpdate(asset=payload["a"], delta=payload["d"])

        def position_update(self, payload):
            """ @todo
            return Message(
                Type=MessageType.UPDATE_POSITION,
                Msg={
                    balance["a"]: Position(
                        Locked=float(balance["l"]),
                        Free=float(balance["f"])
                    ) for balance in payload["B"]
                }
            )
            """
            pass

        def order_report(self, payload):
            # @todo - never did work out how to handle these.
            pass

    def connect(self, creds: Credentials):
        self.client = Client(creds['key'], creds['secret'])
        self.socket_manager = BinanceSocketManager(self.client)

        self.user_transformer = self.UserStreamEventTransformer()
        self.market_transformer = (
            self.MarketStreamPandasTransformer() if self.use_pandas
            else self.MarketStreamRawTransformer()
        )

    def monitor_user(self):
        # get initial account state from the API and dispatch associated event
        self.sync_queue.put(self.transformer.initial_rest_payload(
            self.client.get_account()
        ))

        # subscribe to all subsequent user events
        self.socket_manager.start_user_socket(
            lambda p: self.sync_queue.put(self.user_transformer(p))
        )

    def run(self, symbol: str, process: Callable):
        self.socket_manager.start_symbol_ticker_socket(
            symbol, lambda p: process(self.market_transformer(p))
        )


"""
    # @todo - these will come via execute(TransactionParams)
    def buy(self, asset, amount, limit=False, price=0):
        if limit:
            self.binance.order_limit_buy(
                symbol=asset,
                quantity=amount,
                price=price)
        else:
            self.binance.order_market_buy(
                symbol=asset,
                quantity=amount)

        do we want to return an identifier associated with the transaction
        to allow monitoring via the event stream? I think so?

    # @todo - these will be events.
    def sell(self, asset, amount, limit=False, price=0):
        if limit:
            self.binance.order_limit_sell(
                symbol=asset,
                quantity=amount,
                price=price)
        else:
            self.binance.order_market_sell(
                symbol=asset,
                quantity=amount)
"""
