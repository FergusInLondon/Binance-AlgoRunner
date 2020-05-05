from algorunner.events import UpdateType

from test.helpers import *
from test.adapters.binance.fixtures import *


_FIXTURE_PATTERN = "test/fixtures/binance/{fixture}.json"
ACCOUNT_UPDATE_PATTERN = _FIXTURE_PATTERN.format(fixture="account")
BALANCE_UPDATE_PATTERN = _FIXTURE_PATTERN.format(fixture="balance_update")
EXECUTION_REPORT_PATTERN = _FIXTURE_PATTERN.format(fixture="execution_report")
ACCOUNT_INFORMATION_PATTERN = _FIXTURE_PATTERN.format(fixture="outbound_account_info")
ACCOUNT_POSITION_PATTERN = _FIXTURE_PATTERN.format(fixture="outbound_account_position")


def check_position(positions, symbol, free, locked):
    assert symbol in positions
    assert positions[symbol].Free == free
    assert positions[symbol].Locked == locked


def test_account_transformation(user_transformer, load_fixture):
    with load_fixture(ACCOUNT_UPDATE_PATTERN) as account_payload:
        transformed = user_transformer.initial_rest_payload(account_payload)

    assert not transformed['CanDeposit']
    assert transformed['CanTrade']
    assert transformed['CanWithdraw']

    assert len(transformed['Positions']) == 2
    check_position(transformed['Positions'], 'BTC', 4723846.89208129, 0.0)
    check_position(transformed['Positions'], 'LTC', 4763368.68006011, 0.0)


def test_stream_balance_update_transformation(user_transformer, load_fixture):
    with load_fixture(BALANCE_UPDATE_PATTERN) as balance:
        update_type, update_object = user_transformer(balance)

    assert update_type == UpdateType.BALANCE
    assert update_object['Asset'] == 'BTC'
    assert update_object['Update'] == 100.0


def stream_execution_report_transformation(user_transformer, load_fixture):
    with load_fixture(EXECUTION_REPORT_PATTERN) as execution:
        update_type, update_object = user_transformer(execution)

    pass # @todo - transformation not implemented


def test_stream_account_info_transformation(user_transformer, load_fixture):
    with load_fixture(ACCOUNT_INFORMATION_PATTERN) as information:
        update_type, update_object = user_transformer(information)
    
    assert update_type == UpdateType.ACCOUNT

    assert update_object['CanDeposit']
    assert update_object['CanTrade']
    assert update_object['CanWithdraw']

    assert len(update_object['Positions']) == 5
    check_position(update_object['Positions'], 'LTC', 17366.18538083, 0.0)
    check_position(update_object['Positions'], 'BTC', 10537.85314051, 2.19464093)
    check_position(update_object['Positions'], 'ETH', 17902.35190619, 0.0)
    check_position(update_object['Positions'], 'BNC', 1114503.29769312, 0.0)
    check_position(update_object['Positions'], 'NEO', 0.0, 0.0)


def stream_account_position_transformation(user_transformer, load_fixture):
    with load_fixture(ACCOUNT_POSITION_PATTERN) as position:
        update_type, update_object = user_transformer(position)

    assert update_type == UpdateType.POSITION
    assert "BTC" in update_object
    assert update_object["BTC"].Free
    assert update_object["BTC"].Locked
