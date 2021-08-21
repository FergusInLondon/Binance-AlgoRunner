from algorunner.adapters.base import (
    factory,
    register_adapter
)
from algorunner.adapters.messages import AdapterError
from algorunner.adapters._binance import BinanceAdapter
from queue import Queue


class invalid_adapter:
    """ i do not have an identifier """
    pass

class duplicate_adapter:
    identifier = "binance"
    pass

def test_registry_requires_valid_identifier():
    have_exception = False
    try:
        register_adapter(invalid_adapter)
    except AdapterError:
        have_exception = True

    assert have_exception

def test_registry_rejects_duplicate_adapters():
    have_exception = False
    try:
        register_adapter(invalid_adapter)
    except AdapterError:
        have_exception = True

    assert have_exception

def test_factory_fails_when_adapter_is_unknown():
    have_exception = False
    try:
        factory("notarealadapter", sync_queue=Queue())
    except AdapterError:
        have_exception = True

    assert have_exception

def test_factory_returns_valid_adapter():
    adapter = factory("binance", sync_queue=Queue())
    assert isinstance(adapter, BinanceAdapter)
