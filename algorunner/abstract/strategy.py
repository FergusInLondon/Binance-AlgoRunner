from abc import ABC, abstractmethod

import pandas as pd


class Strategy(ABC):
    """
    A `Strategy` is the container for an algorithm, it simply needs to respond
    to incoming market payloads and be able to generate events for the `Account`
    Actor.
    """
    @abstractmethod
    def process(self, tick: pd.DataFrame):
        """
        @todo - accept Union[pd.DataFrame, RawMarketPayload]
            where RawMarketPayload is a TypedDict w/ no pandas processing.
        """
        pass

    def dispatch(self):
        """
        @todo - fire events to the Actor queue. Concrete implementation.
        """
        pass
