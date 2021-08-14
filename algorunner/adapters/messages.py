from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union

import pandas as pd


class OrderType(Enum):
    MARKET_SELL = 1
    LIMIT_SELL = 2
    MARKET_BUY = 3
    LIMIT_BUY = 4


@dataclass
class RawTickPayload:
    pass


Tick = Union[pd.DataFrame, RawTickPayload]


class AdapterError(Exception):
    pass


class InvalidOrder(Exception):
    """Is LIMIT without price? @todo"""

    pass


class InvalidPayloadError(Exception):
    """InvalidPayloadError is thrown when an invalid message is recieved
    from the exchange via a websocket stream."""

    pass


@dataclass
class Credentials:
    """Required credentials to authenticate with a given exchange."""

    exchange: str
    key: str
    secret: str


@dataclass
class TransactionRequest:
    """Dispatched by `process` this triggers risk calculation via `authorise`
    and potential dispatch of a transaction to the exchange."""

    reason: Optional[str]
    symbol: str
    order_type: OrderType
    quantity: float
    price: Optional[float]
    approved: bool = False
    run_test: bool = True

    def is_limit(self) -> bool:
        return self.order_type in [OrderType.LIMIT_SELL, OrderType.LIMIT_BUY]

    def validate(self):
        if self.is_limit() and not self.price:
            raise InvalidOrder("limit order requires a price")

        if not all([self.symbol, self.order_type, self.quantity]):
            raise InvalidOrder(
                "order requires all of symbol, order_type, and quantity"
            )


@dataclass
class OrderStatus:
    pass
