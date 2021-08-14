from importlib import import_module
from typing import Optional

from loguru import logger

from algorunner.strategy import BaseStrategy
from algorunner.strategy.exceptions import (
    FailureLoadingStrategy, InvalidStrategyProvided, StrategyNotFound
)


_DEFAULT_STRATEGY_PARENT_MODULE = 'strategies.{module}'


def load_strategy(strategy_name: str, module_name: Optional[str] = None) -> BaseStrategy:
    """Dynamically load strategies located in the `/strategies` directory"""
    if not module_name:
        logger.debug("using default module name - looking in strategies directory")
        module_name = _DEFAULT_STRATEGY_PARENT_MODULE.format(
            module=strategy_name.lower()
        )

    try:
        module = import_module(module_name)

        _class = getattr(module, strategy_name)
        if not issubclass(_class, BaseStrategy):
            raise InvalidStrategyProvided()

        return _class()
    except InvalidStrategyProvided as e:
        raise e
    except ModuleNotFoundError:
        raise StrategyNotFound()
    except Exception as e:
        raise FailureLoadingStrategy(strategy_name, e)
