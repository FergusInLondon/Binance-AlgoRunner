@mock_logger
Feature: Hooks
  Hooks allow user-defined handlers to internal events in the AlgoRunner.

  Scenario: An invalid handler should be rejected
    Given no handlers are registered
      and a handler that isn't callable
     When that handler is registered
     Then an InvalidHookHandler exception is raised

  Scenario: Hook type should be validated when registering handler
    Given no handlers are registered
      and a valid handler for an unknown hook
     When that handler is registered
     Then an InvalidHookHandler exception is raised

  @intercepts_error
  Scenario: Invalid handler signactures trigger logging warning
    Given no handlers are registered
    Given an invalid handler with a different signature
      and logging is enabled
     When that handler is registered
      and the process_duration hook is triggered
     Then the logger recieves an error message

  Scenario: A valid hook should be registered and triggered
    Given no handlers are registered
    Given a valid handler for process_duration
     When that handler is registered
      and the process_duration hook is triggered
     Then no exception should be raised
      and the logger recieves no errors
      and the handler should be called
      and the handler should have the correct argument

  Scenario: Multiple hooks should all be called
    Given no handlers are registered
      and 5 valid handlers for process_duration 
     When those handlers are registered
      and the process_duration hook is triggered
     Then no exception should be raised
      and the logger recieves no errors
      and the handlers should all be called
      and the handlers should have the correct argument

  Scenario: Handlers should be called per-hook trigger
    Given no handlers are registered
      and a valid handler for process_duration
     When that handler is registered
      and the process_duration hook is triggered 5 times
     Then no exception should be raised
      and the logger recieves no errors
      and the handler should be called 5 times
