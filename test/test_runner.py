
from signal import SIGTERM
from unittest.mock import MagicMock, patch

from algorunner.adapters import Credentials
from algorunner.adapters.messages import AdapterError
from algorunner.runner import Runner


def test_handle_graceful_shutdown(mock_adapter: MagicMock, mock_strategy: MagicMock):
    with patch('algorunner.runner.signal') as mock_signal:
        r = Runner(
            creds=Credentials(exchange="binance", key="", secret=""),
            strategy=mock_strategy
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
        Runner(Credentials(exchange="lolnoexchange"), mock_strategy)
    except AdapterError:
        have_exception = True

    assert have_exception 
