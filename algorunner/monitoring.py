from time import time

from loguru import logger


class Timer:
    """Simple timer based context manager, used for performance monitoring
       in conjunction with hooks."""
    def __init__(self):
        self.duration = None

    def __enter__(self):
        self.start = time()

    def __exit__(self, exc_type, exc_val, traceback):
        self.duration = (time() - self.start)

        if exc_type:
            logger.error(f"detected exception during monitoring: {exc_type} ({exc_val})")

    def ms(self) -> float:
        return self.duration * 1000
