"""
    .. include:: pdoc.md
"""

from algorunner.strategy.base import BaseStrategy
from algorunner.adapters.base import Adapter
from algorunner.hooks import (
    Hook, InvalidHookHandler, hook, clear_handlers
)
from algorunner.monitoring import Timer

__docformat__ = "restructuredtext"
__all__ = [
    'BaseStrategy',
    'Adapter',
    'Hook',
    'InvalidHookHandler',
    'hook',
    'clear_handlers',
    'Timer',
]