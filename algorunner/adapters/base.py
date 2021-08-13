from abc import ABC, abstractmethod
from typing import Callable, TypedDict
from queue import Queue

from loguru import logger


class AdapterError(Exception):
    pass


class InvalidPayloadRecieved(Exception):
    """InvalidPayloadRecieved is thrown when an invalid message is recieved
       from the exchange via a websocket stream."""
    pass


class Credentials(TypedDict):
    """Required credentials to authenticate with a given exchange."""
    exchange: str
    key: str
    secret: str


class TransactionParams(TypedDict):
    """Parameters detailing an execution to execute on an exchange."""
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
    def execute(self, trx: TransactionParams) -> bool:
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
