from algorunner.hooks import Hook, hook
from queue import Queue
from signal import SIGTERM, signal

from loguru import logger

from algorunner.strategy import BaseStrategy
from algorunner.adapters import Credentials, factory


class Runner(object):
    """
    The Runner is responsible for configuring all components required to execute
    a trading algorithm. It's called by the entrypoint of the app, located in
    `run.py`.
    """

    def __init__(self,
                 creds: Credentials,
                 strategy: BaseStrategy):
        self.sync_queue = Queue()
        self.adapter = factory(creds.exchange, self.sync_queue)
        self.strategy = strategy

        self.strategy.start_sync(self.sync_queue, self.adapter)
        self.adapter.connect(creds)
        signal(SIGTERM, self._handle_sigterm())
        hook(Hook.RUNNER_INITIALISED)

    def _handle_sigterm(self):
        def _handler(signum, frame):
            logger.warning("caught SIGTERM: attempting graceful termination")
            self.stop()

        return _handler

    def run(self):
        """ """
        self.adapter.monitor_user(self.trader_queue)
        self.adapter.run(self.strategy, self.strategy)
        hook(Hook.RUNNER_STARTING)

    def stop(self):
        hook(Hook.RUNNER_STOPPING)
        self.strategy.shutdown()
        self.adapter.disconnect()
