# AlgoRunner

A lightweight service for running algorithmic trading strategies against cryptocurrency exchanges. Currently under heavy development and defining the exchange interactions, as well moving towards support for multiple exchanges.

All development is done against the `develop` branch, although at this time that's likely the branch you actually want to browse.

| Branch  | Status                                                       |
| ------- | ------------------------------------------------------------ |
| Master  | ![Unit Tests & Build](https://github.com/FergusInLondon/Runner/actions/workflows/pythonapp.yml/badge.svg)![CodeQL](https://github.com/FergusInLondon/Runner/actions/workflows/codeql-analysis.yml/badge.svg) |
| Develop | ![Unit Tests & Build](https://github.com/FergusInLondon/Runner/actions/workflows/pythonapp.yml/badge.svg?branch=develop)![CodeQL](https://github.com/FergusInLondon/Runner/actions/workflows/codeql-analysis.yml/badge.svg?branch=develop) |

## Defining a strategy

To define a strategy to execute you simply need to define a `Strategy` class and place it in the `./strategies` folder where it can be loaded. A strategy **must** inherit from `BaseStrategy` and **must** implement two methods: `process` and `authorise`.

```python
import pandas as pd

from algorunner.abstract import BaseStrategy
from algorunner.abstract.base_strategy import (
    AccountState, TransactionRequest, AuthorisationDecision
)


class Example(BaseStrategy):
    def __init__(self):
        self.series = pd.DataFrame
        super().__init__()

    def process(self, tick: pd.DataFrame):
      	"""process accepts a DataFrame containing the latest tick data."""
        self.series = self.series.append(tick)

        if self.series.shape[0] > 5:
            recent_window = pd.to_numeric(self.series[-5:]["PriceChange"])
            print("Average price change over past 5 windows: ", recent_window.mean())

    def authorise(self, state: AccountState, trx: TransactionRequest) -> AuthorisationDecision:
      	"""authorise is used to perform any risk calculations and position sizing."""
        pass
```

From the `BaseStrategy` class you can interact with the market via calling `self.open_position(symbol: str)` and `self.close_position(symbol: str)` - this will subsequently be passed through to the `authorise(...)` call which will determine whether that interaction is allowed, whether it fits in with the users defined approach to risk, and what size the that position should be. Under the hood this is all handles via events.

For information on the classes used - i.e. `AuthorisationDecision`, `TransactionRequest`, and `AccountState` - please see the API documentation.

## Required Configuration

Configuration can be done via: a `.ini` file, environment variables, or a combination of both.

```
[credentials]
exchange = binance             # Identifier of the target exchange.
api_key = binanceAPIKey        # API Key for the exchange
api_secret = binanceAPISecret  # API Secret for the exchange

[strategy]
name = Example     # Strategy to execute
symbol = BTCUSDT   # Symbol to execute the strategy against
```

By default AlgoRunner will try and read a file named `bot.ini`, but this can be overridden by the `--config` flag:

```
$ python run.py --config [config .ini file]
```

Alternatively, configuration can also be done via: a `.ini` file, environment variables, or a combination of both. 

| `.ini` variable        | environment variable  | CLI flag         |
| ---------------------- | --------------------- | ---------------- |
| credentials.exchange   | ALGORUNNER_EXCHANGE   | --exchange       |
| credentials.api_key    | ALGORUNNER_API_KEY    | --api-key        |
| credentials.api_secret | ALGORUNNER_API_SECRET | --api-secret     |
| strategy.name          | -                     | -s / --strategy  |
| strategy.symbol        | -                     | --trading-symbol |

**It's advisable not to pass any exchange details - i.e. `credentials.*`  variables - via either the configuration file or the CLI!**

## Executing AlgoRunner

There are to methods to run AlgoRunner: the recommended way is via Docker.

### Using Docker

To build a Docker Image simply run `make docker` from the root of this repository; this will create an image with the tags `algorunner:<commit-hash>` and `algorunner:latest`, before running the image. **There are no pre-built Docker Images available.**

```
$ make docker # that's genuinely it, I promise.
```

### Running Locally

To run the service locally it's also relatively trivial:

```
$ make deps  # this will install all dependencies
$ make local # this will run the service in the environment provided by poetry
```

Note: you **must** have `poetry` - a python dependency manager - installed on your system to run AlgoRunner. If you don't then the `deps` target of the Makefile will *attempt* to install it on your behalf.

## Development

For details on development please see `DEVELOPMENT.md`, and for details on the automated test suite please see `test/TESTING.md`.

## License

This software is licensed by the terms outlined in the [*The MIT License*](https://opensource.org/licenses/MIT). For the full and entire text of this license please see `LICENSE.txt`.
