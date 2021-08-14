from algorunner.hooks import Hook, hook
from time import time
from typing import Optional

from loguru import logger


class Timer:
    """Simple timer based context manager, used for performance monitoring
       in conjunction with hooks."""
    def __init__(self, trigger_hook: Optional[Hook] = None):
        self.duration = None
        self.hook = trigger_hook

    def __enter__(self):
        self.start = time()

    def __exit__(self, exc_type, exc_val, traceback):
        self.duration = (time() - self.start)

        if exc_type:
            logger.error(f"detected exception during monitoring: {exc_type} ({exc_val})")

        if self.hook:
            hook(self.hook, self.ms())

    def ms(self) -> float:
        return round(self.duration * 1000)
