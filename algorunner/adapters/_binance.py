from logging import getLogger
from typing import Tuple

from binance.client import Client
from binance import BinanceSocketManager
import pandas as pd


from algorunner.abstract.strategy import Strategy
from algorunner.adapters.base import (
    Adapter, Credentials, InvalidPayloadRecieved
)
from algorunner.trader import Trader
from algorunner.events import (
    AccountStatus,
    BalanceUpdate,
    Position,
    PositionStatus,
    UpdateEvent,
    UpdateType
)


logger = getLogger()


class BinanceAdapter(Adapter):
    """ """

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

        def __call__(self, payload) -> Tuple[str, UpdateEvent]:
            try:
                message_map = {
                    "outboundAccountInfo": self.account_update,
                    "outboundAccountPosition": self.position_update,
                    "balanceUpdate": self.balance_update,
                    "executionReport": self.order_report
                }

                return message_map[payload["e"]](payload)
            except KeyError:
                msg = "unknown payload type {p}".format(p=payload.get("e"))
                raise InvalidPayloadRecieved(msg)
            except Exception as e:
                raise Exception("unknown error occured in user stream", e)

        def initial_rest_payload(self, payload) -> AccountStatus:
            # @todo - there is so much data in this payload that we're missing
            # out on, like commission rates etc.
            return AccountStatus(
                CanWithdraw=payload["canWithdraw"],
                CanTrade=payload["canTrade"],
                CanDeposit=payload["canDeposit"],
                Positions={
                    balance["asset"]: Position(
                        Locked=float(balance["locked"]),
                        Free=float(balance["free"])
                    ) for balance in payload["balances"]
                }
            )

        def account_update(self, payload) -> Tuple[str, AccountStatus]:
            return UpdateType.ACCOUNT, AccountStatus(
                CanWithdraw=payload["W"],
                CanTrade=payload["T"],
                CanDeposit=payload["D"],
                Positions={
                    balance["a"]: Position(
                        Locked=float(balance["l"]),
                        Free=float(balance["f"])
                    ) for balance in payload["B"]
                }
            )

        def balance_update(self, payload) -> Tuple[str, BalanceUpdate]:
            return UpdateType.BALANCE, BalanceUpdate(
                Asset=payload["a"], Update=float(payload["d"])
            )

        def position_update(self, payload) -> Tuple[str, PositionStatus]:
            return UpdateType.POSITION, {
                balance["a"]: Position(
                    Locked=float(balance["l"]),
                    Free=float(balance["f"])
                ) for balance in payload["B"]
            }

        def order_report(self, payload):
            # @todo - never did work out how to handle these.
            pass

    def connect(self, creds: Credentials, trader: Trader):
        self.trader = trader
        self.client = Client(creds['key'], creds['secret'])
        self.socket_manager = BinanceSocketManager(self.client)

        self.user_transformer = self.UserStreamEventTransformer()
        self.market_transformer = self.MarketStreamPandasTransformer()
        update = self.transformer.initial_rest_payload(
            self.client.get_account()
        )
        self.trader(UpdateType.ACCOUNT, update)

        self.socket_manager.start_user_socket(self.handle_user_stream)

    def run(self, strategy: Strategy, symbol: str):
        self.strategy = strategy
        self.socket_manager.start_symbol_ticker_socket(
            symbol, self._handle_ticker
        )

    def _handle_ticker(self, tick):
        """Given an incoming payload from the market websocket stream,
           prepare it for the `Strategy` and then execute the strategy
           against it."""
        try:
            parsed_data = self.market_transformer(tick)
            self.strategy.process(parsed_data)
        except InvalidPayloadRecieved as e:
            logger.warn(
                "received exception when handling market stream. ignoring tick.",
                e
            )

    def _handle_user_stream(self, payload):
        try:
            update_type, transformed = self.user_transformer(payload)
            self.account(update_type, transformed)
        except Exception as e:
            logger.warn(
                "recieved exception handling user stream payload. ignoring message.",
                e
            )
