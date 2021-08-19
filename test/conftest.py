from contextlib import contextmanager
from json import load
from unittest.mock import MagicMock, patch

import pytest

from algorunner.strategy import BaseStrategy, load_strategy

@pytest.fixture
def mock_adapter() -> MagicMock:
    with patch('algorunner.runner.factory') as mock:
        mock.return_value = MagicMock()
        yield mock.return_value

@pytest.fixture
def mock_strategy() -> MagicMock:
    abstractmethods = BaseStrategy.__abstractmethods__
    BaseStrategy.__abstractmethods__ = {}

    yield MagicMock()

    BaseStrategy.__abstractmethods__ = abstractmethods

@pytest.fixture
def example_strategy() -> BaseStrategy:
    yield load_strategy('Example')

@pytest.fixture
def load_fixture():
    @contextmanager
    def open_fixture(payload_file):
        with open(payload_file) as json_file:
            yield load(json_file)
    
    return open_fixture
