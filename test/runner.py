import unittest
import json
import pandas as pd
from unittest.mock import patch
from runner import Runner


def get_payload(fixture):
    with open(f"test/fixtures/{fixture}.json") as json_file:
        data = json.load(json_file)
    return data


class MockStrategy(object):
    def start(self, control):
        self.control = control


example_kline = {
    'e': '24hrTicker',
    'E': 1580770073221,
    's': 'BTCUSDT',
    'p': '-117.45000000',
    'P': '-1.250',
    'w': '9362.96596369',
    'x': '9394.08000000',
    'c': '9276.63000000',
    'Q': '0.01075500',
    'b': '9275.46000000',
    'B': '0.26951100',
    'a': '9276.63000000',
    'A': '0.00002400',
    'o': '9394.08000000',
    'h': '9618.79000000',
    'l': '9234.00000000',
    'v': '52160.24254000',
    'q': '488374575.55996477',
    'O': 1580683673213,
    'C': 1580770073213,
    'F': 238122539,
    'L': 238624515,
    'n': 501977
}


class TestRunner(unittest.TestCase):

    @patch('runner.Client', autospec=True)
    @patch('runner.BinanceSocketManager', autospec=True)
    def test_runner_init(self, socket_mock, client_mock):
        """
            Ensure that the runner initialises by (a) creating a Binance API client,
            (b) retrieving account details, and (c) starting a User Websocket Conn.
        """
        client_instance = client_mock.return_value
        client_instance.get_account.return_value = get_payload("account")

        r = Runner("apiKey", "apiSecret", "symbol", None)

        client_mock.assert_called_once_with("apiKey", "apiSecret")
        client_instance.get_account.assert_called_once()
        socket_mock.return_value.start_user_socket.assert_called_once()

    @patch('runner.Client', autospec=True)
    @patch('runner.BinanceSocketManager', autospec=True)
    def test_runner_run(self, socket_mock, client_mock):
        """
            Ensure that `.start()` is called on the strategy, that the correct args
            are provided to the new streaming ticker socket, and that the socket is
            correctly started.
        """
        mock_strategy = MockStrategy()
        client_instance = client_mock.return_value
        client_instance.get_account.return_value = get_payload("account")

        r = Runner("apiKey", "apiSecret", "symbolToMonitor", mock_strategy)
        r.run()

        self.assertEqual(mock_strategy.control, r)

        call = socket_mock.return_value.start_symbol_ticker_socket.call_args_list
        self.assertEqual(call[0][0][0], "symbolToMonitor")
        socket_mock.return_value.start.assert_called_once()

    @patch('runner.Client', autospec=True)
    @patch('runner.BinanceSocketManager', autospec=True)
    def test_parse_dataframe(self, socket_mock, client_mock):
        """
            Ensure that inbound kline messages are correctly parsed in to Pandas
            dataframes.
        """

        df = Runner.parse_dataframe(example_kline)
        self.assertFalse(df.empty)
        self.assertEqual(df.shape, (1, 22))
        self.assertEqual(df.index.name, "EventTime")

        # a few random columns
        self.assertEqual(df["OpenPrice"][0], '9394.08000000')
        self.assertEqual(df["PriceChangePercent"][0], '-1.250')
        self.assertEqual(df["LastQuantity"][0], '0.01075500')

if __name__ == "__main__":
    unittest.main()
