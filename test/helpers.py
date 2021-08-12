from contextlib import contextmanager
from json import load
from pytest import fixture


@fixture
def load_fixture():
    @contextmanager
    def open_fixture(payload_file):
        with open(payload_file) as json_file:
            yield load(json_file)
    
    return open_fixture
