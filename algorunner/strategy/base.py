from abc import ABC, abstractmethod
from algorunner.hooks import Hook, hook, hook_handler
from queue import Queue
from threading import Thread
from typing import Callable, Dict, Optional

from loguru import logger

from algorunner.strategy.exceptions import StrategyExceptionThresholdBreached

from algorunner.monitoring import Timer
from algorunner.mutations import AccountState, is_update
from algorunner.adapters.base import Adapter
from algorunner.adapters.messages import (
    InvalidOrder,
    OrderType,
    TransactionRequest,
    Tick,
)


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

    class _SyncAgent:
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

            exception_count = 0  # @todo count exceptions over past 5 mins. Probs a job for a contextmanager.
            while True:
                message = self.queue.get()
                message_type = type(message)

                try:
                    if message_type == ShutdownRequest:
                        logger.warning(
                            f"terminating trader thread ({message.reason})."
                        )
                        break
                    elif message_type == TransactionRequest:
                        logger.info(
                            "request recieved from strategy to execute a transaction"
                        )
                        self._transaction_handler(message)
                        continue
                    elif not is_update(message_type):
                        logger.error("recieved message without known handler")
                        continue

                    message.handle(self.state)
                except Exception as e:
                    logger.error(
                        "sync agent has caught an exception. will try to continue.",
                        {
                            "exc": e,
                            "exc_count": exception_count,
                        },
                    )

                    if exception_count > 5:
                        logger.critical(
                            "exception rate has breached threshold, failing.."
                        )
                        raise StrategyExceptionThresholdBreached(
                            "too many exceptions encountered!"
                        )

            logger.warn("syncagent has completed")

        def _transaction_handler(self, trx: TransactionRequest):
            trx = self.authorisation_guard(self.state, trx)
            if not trx.approved:
                logger.info(f"transaction rejected: {trx.reason}")
                return

            t = Timer(Hook.API_EXECUTE_DURATION)
            with t:
                try:
                    logger.info(
                        "transaction accepted: passing to API adapter for dispatch"
                    )
                    self.api.execute(trx)
                except InvalidOrder:
                    pass

    def __call__(self, tick: Tick):
        t = Timer(Hook.PROCESS_DURATION)
        with t:
            self.process(tick)

    def start_sync(self, queue: Queue, adapter: Adapter):
        self.sync_agent = self._SyncAgent(queue, adapter, self.log)
        self.sync_queue = queue

    def _place_order(self, params: dict):
        try:
            params = TransactionRequest(**params)
            self.sync_queue.put(params)
            hook(Hook.ORDER_REQUEST, params)
        except TypeError:
            raise InvalidOrder(
                "invalid parameters supplied when attempting order"
            )

    def order_sell_limit(self, **kwargs):
        if not all([kwargs["symbol"], kwargs["price"], kwargs["quantity"]]):
            raise InvalidOrder(
                "order_sell_limit requires symbol, price, and quantity"
            )

        self._place_order({**kwargs, **{"order_type": OrderType.LIMIT_SELL}})

    def order_sell_market(self, **kwargs):
        if not all([kwargs["symbol"], kwargs["quantity"]]):
            raise InvalidOrder("order_sell_market requires symbol and quantity")

        self._place_order({**kwargs, **{"order_type": OrderType.MARKET_SELL}})

    def order_buy_limit(self, **kwargs):
        if not all([kwargs["symbol"], kwargs["price"], kwargs["quantity"]]):
            raise InvalidOrder(
                "order_buy_limit requires symbol, price, and quantity"
            )

        self._place_order({**kwargs, **{"order_type": OrderType.LIMIT_BUY}})

    def order_buy_market(self, **kwargs):
        if not all([kwargs["symbol"], kwargs["quantity"]]):
            raise InvalidOrder("order_buy_market requires symbol and quantity")

        self._place_order({**kwargs, **{"order_type": OrderType.MARKET_SELL}})

    def shutdown(self):
        self.sync_agent.stop("shutdown requested")

    def account_state(self) -> AccountState:
        return self.sync_agent.account_state

    def register_hooks(self, hooks: Dict[Hook, Callable]):
        def wrapper(fn):
            def _wrapped(*args, **kwargs):
                fn(*args, **kwargs)

            return _wrapped

        for h in hooks:
            hook_handler(h)(wrapper(hooks[h]))

    def authorise(
        self, state: AccountState, trx: TransactionRequest
    ) -> TransactionRequest:
        logger.info(
            "no authorisation guard set: automatically authorising order"
        )
        trx.approved = True
        return trx

    @abstractmethod
    def process(self, tick: Tick):
        """ """
        pass
