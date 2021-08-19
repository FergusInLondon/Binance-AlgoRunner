from behave import *

from algorunner.hooks import (
    hook_handler, clear_handlers, hook,
    Hook, InvalidHookHandler
)


class not_callable():
    pass


def has_wrong_signature(ex: str, am: int, ple: dict) -> int:
    return 5


class valid_handler:
    def __init__(self):
        self.was_called = False
        self.arg = None
        self.call_times = 0

    def __call__(self, duration: float) -> None:
        self.call_times += 1
        self.was_called = True
        self.arg = duration


## GIVEN 


@given(u'no handlers are registered')
def no_registered_handlers(context):
    clear_handlers()

@given(u'a handler that isn\'t callable')
def non_callable_handler(context):
    context.handlers = [not_callable()]

@given(u'{num:d} valid handlers for process_duration')
def multiple_valid_handlers(context, num):
    context.handlers = [valid_handler() for _ in range(num)]

@given(u'an invalid handler with a different signature')
def wrong_signature_handler(context):
    context.handlers = [has_wrong_signature]

@given(u'a valid handler for an unknown hook')
def valid_handler_unknown_hook(context):
    context.hook = "ewfgheruihuier"
    context.handlers = [valid_handler()]

@given(u'a valid handler for process_duration')
def valid_process_duration_handler(context):
    context.handlers = [valid_handler()]


## WHEN


@when(u'that handler is registered')
def handler_registered(context):
    handlers_registered(context)

@when(u'the process_duration hook is triggered')
def trigger_hook(context):
    context.logger_has_error = False
    context.hook_param = 3.242

    context.mock_logger.error.call_count = 0
    hook(Hook.PROCESS_DURATION, context.hook_param)
    context.logger_has_error = (context.mock_logger.error.call_count == 1)

@when(u'those handlers are registered')
def handlers_registered(context):
    context.have_exception = False
    context.have_hook_exception = False

    try:
        register_fn = hook_handler(getattr(context, "hook", Hook.PROCESS_DURATION))        
        for handler in context.handlers:
            register_fn(handler)
    except InvalidHookHandler:
        context.have_exception = True
        context.have_hook_exception = True
    except Exception:
        context.have_exception = True

@when(u'the process_duration hook is triggered {times:d} times')
def step_impl(context, times):
    for _ in range(times):
        trigger_hook(context)

@given(u'logging is enabled')
def logging_enabled(context):
    pass


## THEN


@then(u'an InvalidHookHandler exception is raised')
def hook_handler_exception_raised(context):
    assert context.have_hook_exception

@then(u'the handlers should have the correct argument')
def handlers_argument(context):
    for handler in context.handlers:
        assert handler.arg == context.hook_param

@then(u'the handler should have the correct argument')
def handler_argument(context):
    handlers_argument(context)

@then(u'no exception should be raised')
def no_exception_raised(context):
    assert not context.have_exception

@then(u'the handlers should all be called')
def handlers_called(context):
    for handler in context.handlers:
        assert handler.was_called

@then(u'the handler should be called')
def handler_called(context):
    handlers_called(context)

@then(u'the handler should be called {times:d} times')
def handler_called_multiple_times(context, times):
    for handler in context.handlers:
        assert handler.call_times == times

@then(u'the logger recieves no errors')
def logger_has_no_errors(context):
    assert context.logger_has_error == False

@then(u'the logger recieves an error message')
def logger_has_errors(context):
    assert context.logger_has_error