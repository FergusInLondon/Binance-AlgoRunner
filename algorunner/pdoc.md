> @todo: define *all* user required objects, and then import to `algorunner/__init__.py`
> to simplify document generation *and* developer experience.

AlgoRunner is a simple framework that can be used to build algorithmic trading strategies against cryptocurrency exchanges.

For information on the development, check the [repository](https://github.com/FergusInLondon/Runner).

> **This documentation covers the objects that you'll need to interact with when using AlgoRunner; it doesn't necessarily cover the internals of the system.**

## Using AlgoRunner

AlgoRunner is simple: **Strategy** objects are executed against an exchange via an API **Adapter**.

## Writing Strategies

The abstract methods required to be implemented are located in `algorunner.BaseStrategy`.

### Integration with "Hooks"

AlgoRunner has the concept of "*hooks*": simple events that are dispatched containing performance metrics or status updates. See `algorunner.hooks` for information information about these.

### Exceptions and Error Handling

Check out the `algorunner.exceptions` module for more information.

## Writing Adapters

Adapters must inherit from `algorunner.adapters.base`.
