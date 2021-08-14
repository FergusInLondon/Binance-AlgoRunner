from enum import Enum
from typing import Callable, Optional

from loguru import logger


class Hook(Enum):
    """Hook represents valid hooks for user-defined functions to listen
       for."""
    PROCESS_DURATION = 1
    API_EXECUTE_DURATION = 2


class InvalidHookHandler(Exception):
    """Raised when `hook_handler` is unable to register a given hook."""
    pass


CALLBACK_TYPES = {
    Hook.PROCESS_DURATION: Callable[[float], None],
    Hook.API_EXECUTE_DURATION: Callable[[float], None],
}

# @todo We have a few of these registry decorations now; place in one class?
_registered_hooks = {}


def hook_handler(hook: Hook):
    """`hook_handler` is a decorator to go wrap around a hook handler."""
    def register(fn):
        if not hook:
            raise InvalidHookHandler(f"no hook specified for '{fn.__name}'")

        expected_callback = CALLBACK_TYPES.get(hook)
        if not expected_callback:
            raise InvalidHookHandler(f"unknown hook specified ('{hook}')")

        if not callable(fn):
            raise InvalidHookHandler(f"invalid hook supplied for '{hook}")

        callbacks = _registered_hooks.get(hook, [])
        callbacks.append(fn)
        _registered_hooks[hook] = callbacks

    return register


def hook(hook: Hook, *args, **kwargs):
    """`hook(...)` calls any handlers associated with a given Hook."""
    callbacks = _registered_hooks.get(hook, [])
    for cb in callbacks:
        try:
            cb(*args, **kwargs)
        except TypeError:
            logger.error(f"invalid handler ({cb.__name__}) for hook ({hook})")


def clear_handlers(hook: Optional[Hook] = None):
    """`clear_handlers` clears registered handlers; optionally for
       a specific hook"""
    if hook and _registered_hooks.get(hook):
        _registered_hooks[hook] = []
        return

    _registered_hooks.clear()


@hook_handler(hook=Hook.API_EXECUTE_DURATION)
def handle_api_duration(duration: float):
    logger.debug(f"api execution duration: {duration}ms")


@hook_handler(hook=Hook.PROCESS_DURATION)
def handle_process_duration(duration: float):
    logger.debug(f"tick process duration: {duration}ms")
