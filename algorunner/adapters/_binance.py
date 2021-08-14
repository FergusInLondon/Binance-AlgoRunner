from typing import Callable

from binance.client import Client
from binance import BinanceSocketManager

import pandas as pd

from algorunner.adapters.base import (
    register_adapter, Adapter
)

from algorunner.adapters.messages import (
    Credentials, InvalidOrder, InvalidPayloadError, OrderType, TransactionRequest
)

from algorunner.mutations import (
    AccountUpdate, BaseUpdate, BalanceUpdate, CapabilitiesUpdate, Position
)


@register_adapter
class BinanceAdapter(Adapter):
    """ """

    identifier = "binance"

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
                raise InvalidPayloadError(msg)
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

        def order_endpoint(self, payload):
            # @todo - parse the result from the order endpoint.
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
        self.user_conn_key = self.socket_manager.start_user_socket(
            lambda p: self.sync_queue.put(self.user_transformer(p))
        )

    def run(self, symbol: str, process: Callable):
        self.market_conn_key = self.socket_manager.start_symbol_ticker_socket(
            symbol, lambda p: process(self.market_transformer(p))
        )

    def execute(self, trx: TransactionRequest):
        trx.validate()

        kwargs = {
            "symbol": trx.symbol,
            "quantity": trx.quantity,
        }

        if trx.is_limit():
            kwargs["price"] = trx.price

        dispatcher = {
            OrderType.LIMIT_BUY: self.binance.order_limit_buy,
            OrderType.LIMIT_SELL: self.binance.order_limit_sell,
            OrderType.MARKET_BUY: self.binance.order_market_buy,
            OrderType.MARKET_SELL: self.binance.order_market_sell,
        }.get(trx.order_type)

        if not dispatcher:
            raise InvalidOrder("invalid order type")

        order_response = dispatcher(**kwargs)
        return self.user_transformer.order_endpoint(order_response)

    def disconnect(self):
        self.socket_manager.stop_socket(self.market_conn_key)
        self.socket_manager.stop_socket(self.user_conn_key)
        self.socket_manager.close()
