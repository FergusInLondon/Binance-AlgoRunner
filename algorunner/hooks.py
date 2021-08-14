from algorunner.adapters.messages import TransactionRequest
from enum import Enum
from typing import Callable, Optional

from loguru import logger


class Hook(Enum):
    """Hook represents valid hooks for user-defined functions to listen
    for."""

    RUNNER_INITIALISED = 1
    RUNNER_STARTING = 2
    RUNNER_STOPPING = 3
    ORDER_REQUEST = 4
    API_EXECUTE_DURATION = 5
    PROCESS_DURATION = 6


class InvalidHookHandler(Exception):
    """Raised when `hook_handler` is unable to register a given hook."""

    pass


CALLBACK_TYPES = {
    Hook.PROCESS_DURATION: Callable[[float], None],
    Hook.API_EXECUTE_DURATION: Callable[[float], None],
    Hook.ORDER_REQUEST: Callable[[TransactionRequest], None],
    Hook.RUNNER_STOPPING: Callable[[], None],
    Hook.RUNNER_STARTING: Callable[[], None],
    Hook.RUNNER_INITIALISED: Callable[[], None],
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

        fn.__hook_handler__ = True
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


@hook_handler(hook=Hook.RUNNER_STARTING)
def handle_runner_starting():
    logger.info("runner initiation: monitoring streams and executing strategy")


@hook_handler(hook=Hook.RUNNER_STOPPING)
def handle_runner_stopping():
    logger.info("runner termination: closing streams and terminating strategy")


@hook_handler(hook=Hook.RUNNER_INITIALISED)
def handle_runner_initialisation():
    logger.info("runner is ready for execution")
