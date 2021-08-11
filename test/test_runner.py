from logging import getLogger
from signal import SIGTERM

import pytest
from unittest.mock import MagicMock, patch

from algorunner.abstract import BaseStrategy
from algorunner.adapters import Credentials
from algorunner.exceptions import UnknownExchange
from algorunner.runner import Runner


test_logger = getLogger()


@pytest.fixture
def mock_adapter() -> MagicMock:
    with patch('algorunner.runner.get_adapter') as mock:
        mock.return_value = MagicMock()
        yield mock.return_value

@pytest.fixture
def mock_strategy() -> MagicMock:
    abstractmethods = BaseStrategy.__abstractmethods__
    BaseStrategy.__abstractmethods__ = {}

    yield MagicMock()

    BaseStrategy.__abstractmethods__ = abstractmethods


def test_handle_graceful_shutdown(mock_adapter: MagicMock, mock_strategy: MagicMock):
    with patch('algorunner.runner.signal') as mock_signal:
        r = Runner(
            creds=Credentials(exchange="binance"),
            strategy=mock_strategy,
            logger=test_logger
        )

        # check components are ran
        mock_strategy.start_sync.assert_called_once()
        mock_adapter.connect.assert_called_once()

        # check signal handler is configured
        mock_signal.assert_called_once()
        signal, handler = mock_signal.call_args.args

        # check signal handler terminates components
        handler(SIGTERM, None)
        mock_adapter.disconnect.assert_called_once()
        mock_strategy.shutdown.assert_called_once()


def invalid_exchange_should_trigger_exception(mock_strategy):
    have_exception = False
    try:
        Runner(Credentials(exchange="lolnoexchange"), mock_strategy, test_logger)
    except UnknownExchange:
        have_exception = True

    assert have_exception 
    pass