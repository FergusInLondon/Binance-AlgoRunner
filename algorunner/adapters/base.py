from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional, Union
from queue import Queue

from loguru import logger
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
    """Is LIMIT without price? @todo """
    pass


class InvalidPayloadError(Exception):
    """InvalidPayloadError is thrown when an invalid message is recieved
       from the exchange via a websocket stream."""
    pass


@dataclass
class Credentials():
    """Required credentials to authenticate with a given exchange."""
    exchange: str
    key: str
    secret: str


@dataclass
class TransactionRequest:
    """Dispatched by `process` this triggers risk calculation via `authorise`
    and potential dispatch of a transaction to the exchange."""
    reason: str
    symbol: str
    order_type: OrderType
    quantity: float
    price: Optional[float]
    approved: bool = False

    def is_limit(self) -> bool:
        return self.order_type in [OrderType.LIMIT_SELL, OrderType.LIMIT_BUY]

    def validate(self):
        if self.is_limit() and not self.price:
            raise InvalidOrder("limit order requires a price")

        if not all([self.symbol, self.order_type, self.quantity]):
            raise InvalidOrder("order requires all of symbol, order_type, and quantity")


@dataclass
class OrderStatus:
    pass


class Adapter(ABC):
    """Required interface that an exchange adapter must implement."""

    def __init__(self, sync_queue: Queue):
        self.sync_queue = sync_queue

    @abstractmethod
    def connect(self, creds: Credentials):
        """connect authenticates with the exchange, and also populates
           the associated `Trader` object with the latest state."""
        pass

    @abstractmethod
    def monitor_user(self):
        """ @todo """
        pass

    @abstractmethod
    def run(self, process: Callable, terminated: bool):
        """run executes the underlying strategy, ensuring that any data
           transformation required is carried out correctly."""
        pass

    @abstractmethod
    def execute(self, trx: TransactionRequest) -> bool:
        pass

    @abstractmethod
    def disconnect(self):
        pass


_available_adapters = {}


def register_adapter(cls):
    logger.debug("registering new adapter...")
    try:
        identifier = getattr(cls, "identifier")
    except AttributeError:
        raise AdapterError(f"cannot find identifier for adapter class: {cls.__name__}")

    if hasattr(_available_adapters, identifier):
        raise AdapterError(f"attempt at registering duplicate adapter for identifier: {identifier}")

    _available_adapters[cls.identifier] = cls
    logger.debug(f"registered new adapter: '{identifier}'")
    return cls


def factory(requested_adapter: str, *args, **kwargs) -> Adapter:
    logger.info(f"instantiating adapter for '{requested_adapter}'")
    cls = _available_adapters.get(requested_adapter)
    if not cls:
        raise AdapterError(f"no adapter registered for identifier {requested_adapter}")

    return cls(*args, **kwargs)
