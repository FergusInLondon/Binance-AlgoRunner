from abc import ABC, abstractmethod
from typing import Callable, TypedDict
from queue import Queue


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
