from abc import ABC, abstractmethod
from dataclasses import dataclass
from queue import Queue
from threading import Thread
from typing import Callable, Optional

from loguru import logger
import pandas as pd

from algorunner.exceptions import StrategyExceptionThresholdBreached
from algorunner.mutations import AccountState, is_update
from algorunner.adapters.base import Adapter, TransactionParams


@dataclass
class TransactionRequest:
    """Dispatched by `process` this triggers risk calculation via `authorise`
    and potential dispatch of a transaction to the exchange."""
    symbol: str
    order_type: str


@dataclass
class AuthorisationDecision:
    """Returned by `authorise` and determines whether a transaction can be
    made, and the appropriate parameters for that transaction."""
    accepted: bool
    params: Optional[TransactionParams]


class ShutdownRequest:
    """When recieved by the Sync Agent this triggers thread termination."""
    def __init__(self, reason: str = "unknown reason"):
        self.reason = reason


class BaseStrategy(ABC):
    """
    A `BaseStrategy` is the container for an algorithm, it simply needs to respond
    to incoming market payloads and be able to generate events for the internal
    `SyncAgent` Actor which is responsible for synchronising state between the API
    and the algorithm. (In this context "state" means transactions, balances and
    positions)
    """

    class SyncAgent:
        def __init__(self, queue: Queue, adapter: Adapter, auth: Callable):
            self.queue = queue
            self.api = adapter
            self.state = AccountState()
            self.authorisation_guard = auth

        def start(self):
            # @todo - do we *really* want it as a daemon; I see two arguments here.
            # tests obviously *must* be run against a daemon.
            self.thread = Thread(target=self._listen, daemon=True)
            self.thread.start()
            logger.debug("initiated sync agent")

        def stop(self, reason: Optional[str] = None):
            logger.info(f"sync agent termination requested: '{reason}'")
            self.queue.put(ShutdownRequest(reason))

            self.thread.join()
            logger.info("sync agent has halted.")

        def is_running(self) -> bool:
            return self.thread.is_alive()

        def _listen(self):
            logger.info("listening for events and inbound messages")

            exception_count = 0  # count exceptions over past 5 mins.
            while True:
                message = self.queue.get()
                message_type = type(message)

                try:
                    if message_type == ShutdownRequest:
                        logger.warning(f"terminating trader thread ({message.reason}).")
                        break
                    elif message_type == TransactionRequest:
                        logger.info("request recieved from strategy to execute a transaction")
                        self._transaction_handler(message)
                        continue
                    elif not is_update(message_type):
                        logger.error("recieved message without known handler")
                        continue

                    message.handle(self.state)
                except Exception as e:
                    logger.error("sync agent has caught an exception. will try to continue.", {
                        "exc": e, "exc_count": exception_count,
                    })

                    if exception_count > 5:
                        logger.critical("exception rate has breached threshold, failing..")
                        raise StrategyExceptionThresholdBreached("too many exceptions encountered!")

            logger.warn("trader thread has completed")

        def _transaction_handler(self, trx: TransactionRequest):
            decision = self.authorisation_guard(self.state, trx)
            if not decision.accepted:
                logger.info("transaction rejected: failed defined auth rules")
                return

            logger.info("transaction accepted: passing to API adapter for dispatch")
            self.api.execute(decision.params)

    def start_sync(self, queue: Queue, adapter: Adapter):
        self.sync_agent = self.SyncAgent(queue, adapter, self.log)
        self.sync_queue = queue

    def open_position(self, symbol: str):
        logger.debug(f"requesting to open new position ({symbol})")
        self.sync_queue.put(TransactionRequest(symbol=symbol, order_type="BUY"))

    def close_position(self, symbol: str):
        logger.debug(f"requesting to close position ({symbol})")
        self.sync_queue.put(TransactionRequest(symbol=symbol, order_type="SELL"))

    def shutdown(self):
        self.sync_agent.stop("shutdown requested")

    @abstractmethod
    def process(self, tick: pd.DataFrame):
        """
        @todo - accept Union[pd.DataFrame, RawMarketPayload]
            where RawMarketPayload is a TypedDict w/ no pandas processing.
        """
        pass

    @abstractmethod
    def authorise(self,
                  state: AccountState,
                  trx: TransactionRequest) -> AuthorisationDecision:
        """
        @todo - define params.
        """
        pass
