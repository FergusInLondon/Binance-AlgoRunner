import pandas as pd
from lib.runner import Runner
import configparser

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


if __name__ == "__main__":
    # Example Usage:
    #
    # Instantiate a `Runner`; providing API credentials, the symbol you wish to
    # run your strategy against, and the actual strategy itself. Then simply call
    # `.run()` to execute the strategy.

    cfg = configparser.ConfigParser()
    cfg.read('bot.ini')

    strategy = ExampleStrategy()
    runner = Runner(
        apiKey = cfg['credentials']['ApiKey'],
        apiSecret = cfg['credentials']['ApiSecret'],
        symbol = cfg['strategy']['Symbol'],
        runnable=strategy)
    runner.run()
