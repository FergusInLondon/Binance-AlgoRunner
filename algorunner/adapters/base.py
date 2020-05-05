from abc import ABC, abstractmethod
from typing import TypedDict

from algorunner.abstract.strategy import Strategy
from algorunner.trader import Trader


class InvalidPayloadRecieved(Exception):
    """InvalidPayloadRecieved is thrown when an invalid message is recieved
       from the exchange via a websocket stream."""
    pass


class Credentials(TypedDict):
    """Required credentials to authenticate with a given exchange."""
    exchange: str
    key: str
    secret: str


class Adapter(ABC):
    """Required interface that an exchange adapter must implement."""

    @abstractmethod
    def connect(self, creds: Credentials, trader: Trader):
        """connect authenticates with the exchange, and also populates
           the associated `Trader` object with the latest state."""
        pass

    @abstractmethod
    def run(self, strategy: Strategy):
        """run executes the underlying strategy, ensuring that any data
           transformation required is carried out correctly."""
        pass
