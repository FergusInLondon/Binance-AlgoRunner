# Testing

The living document linked to from the `README` outlines the tests expected/required to run.

## Execution

To run the tests use the `test` make target - i.e `$ make test`.

## Test Types

### BDD Scenarios
The `scenarios` folder contains some BDD style tests - using `behave` - for testing the `Trader` object.

The decision to introduce additional BDD style tests was taken as `Trader` is based around a rough interpretation of the `Actor` model. In real terms this means all interactions go through a concurrent message-style interface; the implementation in this repository utilises `TypedDict` objects named `*Update`, that get dispatched through a `queue.Queue`.


### Unit Tests

This directory contains the unit tests for application, there are notes as to which components require testing - and the various cases that need to be accounted for - detailed in the notion.so document.
