# Runner ![Runner](https://github.com/FergusInLondon/Runner/workflows/Runner/badge.svg)

A massive WIP that may or may not be worth an actual README at this point in time. It has no tests, and the account functionality is still being baked in.

Currently it does invoke a strategy and provides it with real-time streamed data from Binance though.

### Note
This is *vaguely* related to my form of Enigma Catalyst, as (a) I really want to brush up on my Python, and (b) Binance seems like the best exchange to implement streaming trades on - so I'd like to get used to interacting with them.

## Example

Check `example.py` for a runnable version of this strategy:

```python
class ExampleStrategy(object):
    """
        A simple example strategy that computes the average price change over
        the previous 5 2000ms updates. 
    """

    def start(self, control):
        self.series = pd.DataFrame()
        self.control = control

    def process(self, kline):
        self.series = self.series.append(kline)

        if self.series.shape[0] > 5:
            print("Average price change over past 5 windows: ", pd.to_numeric(self.series[-5:]["PriceChange"]).mean())
```

When executed via the runner, this will calculate the average price change over the past 5 2000ms updates, and display it to the user.

```
python example.py
Average price change over past 5 windows:  26.694
Average price change over past 5 windows:  26.356
Average price change over past 5 windows:  26.444
Average price change over past 5 windows:  26.246000000000002
Average price change over past 5 windows:  26.272000000000002
Average price change over past 5 windows:  26.706
Average price change over past 5 windows:  27.142000000000003
Average price change over past 5 windows:  27.182
Average price change over past 5 windows:  27.562
Average price change over past 5 windows:  28.002
Average price change over past 5 windows:  28.246000000000002
Average price change over past 5 windows:  28.49
Average price change over past 5 windows:  28.754
```

---

## August 2021 Update: AlgoRunner V2.0

A preview of this release is available in the [`develop`](https://github.com/FergusInLondon/Runner/tree/develop) branch; and progress tracking is available via the [Version 2 Project Board](https://github.com/FergusInLondon/Runner/projects/1).

This version aims to introduce a new design to allow easier exchange API interactions, concurrent processing of market orders, user definable algorithms *and* risk calculations, and improved dependency management.
