from typing import Optional


class FailureLoadingStrategy(Exception):
    """
    Raised when a Strategy cannot be instantiated; this may be down to
    loading the Strategy, or errors that render it unexecutable. Also
    stores the original exception if available.
    """
    def __init__(self, strategy_name: str, exception: Optional[Exception]):
        self.message = "unable to instantiate strategy '{name}'".format(name=strategy_name)
        self.exc = exception


class InvalidStrategyProvided(Exception):
    """Raised when the loaded strategy does no inherit from the base class."""
    pass


class StrategyNotFound(Exception):
    """Raised when the module loader is unable to retrieve the strategy."""
    pass


class StrategyExceptionThresholdBreached(Exception):
    pass
