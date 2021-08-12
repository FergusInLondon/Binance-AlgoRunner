from queue import Queue
from signal import SIGTERM, signal

from loguru import logger

from algorunner import abstract
from algorunner.adapters import ADAPTERS, Credentials, Adapter
from algorunner.exceptions import UnknownExchange


def get_adapter(exchange: str, *args, **kwargs) -> Adapter:
    adapter_cls = ADAPTERS.get(exchange)
    if not adapter_cls:
        raise UnknownExchange(exchange)

    return adapter_cls(*args, **kwargs)


class Runner(object):
    """
    The Runner is responsible for configuring all components required to execute
    a trading algorithm. It's called by the entrypoint of the app, located in
    `run.py`.
    """

    def __init__(self,
                 creds: Credentials,
                 strategy: abstract.BaseStrategy):
        self.sync_queue = Queue()
        self.adapter = get_adapter(creds["exchange"], self.sync_queue)
        self.strategy = strategy

        self.strategy.start_sync(self.sync_queue, self.adapter)
        self.adapter.connect(creds)
        signal(SIGTERM, self._handle_sigterm())
        logger.debug("finished initialising runner")

    def _handle_sigterm(self):
        def _handler(signum, frame):
            logger.warning("caught SIGTERM: attempting graceful termination")
            self.stop()

        return _handler

    def run(self):
        """ """
        self.adapter.monitor_user(self.trader_queue)
        self.adapter.run(self.strategy, self.strategy.process)
        logger.info("monitoring user stream and executing strategy")

    def stop(self):
        logger.info("attempting to shutdown strategy execution and disconnect from exchange")
        self.strategy.shutdown()
        self.adapter.disconnect()
