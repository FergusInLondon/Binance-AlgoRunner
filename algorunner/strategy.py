from importlib import import_module
from typing import Optional

from algorunner.abstract import Strategy


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


_DEFAULT_STRATEGY_PARENT_MODULE = 'strategies.{module}'


def load_strategy(strategy_name: str, module_name: Optional[str] = None) -> Strategy:
    """Dynamically load strategies located in the `/strategies` directory"""
    if not module_name:
        module_name = _DEFAULT_STRATEGY_PARENT_MODULE.format(
            module=strategy_name.lower()
        )

    try:
        module = import_module(module_name)

        _class = getattr(module, strategy_name)
        if not issubclass(_class, Strategy):
            raise InvalidStrategyProvided()

        return _class()
    except InvalidStrategyProvided as e:
        raise e
    except ModuleNotFoundError:
        raise StrategyNotFound()
    except Exception as e:
        raise FailureLoadingStrategy(strategy_name, e)
