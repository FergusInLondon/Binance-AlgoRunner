import pytest

from algorunner.mutations import *


class NotAnEvent:
    pass


@pytest.mark.parametrize("cls, is_valid", [
    (OrderUpdate, True), (BalanceUpdate, True), (AccountUpdate, True),
    (AccountState, False), (NotAnEvent, False), (NoBalanceAvailable, False)
])
def test_update_objects_registered(cls, is_valid):
    assert is_update(cls) == is_valid


balance_update_cases = [
    (BalanceUpdate(asset="BTC", delta=100), [("BTC", 100.0)]),
    (BalanceUpdate(asset="ETH", delta=33.12), [("BTC", 100.0), ("ETH", 33.12)]),
    (BalanceUpdate(asset="BTC", delta=-53.2), [("BTC", 46.8), ("ETH", 33.12)])
]
def test_balance_update():
    account = AccountState()

    for test in balance_update_cases:
        update, expectations = test
        update.handle(account)

        for e in expectations:
            (free, _) = account.balance(e[0])
            assert free == e[1]


account_update_cases = [
    (
        AccountUpdate(balances=[Position(asset="BTC", free=523.1, locked=32)]),
        [("BTC", 523.1, 32)]
    ),
    (
        AccountUpdate(balances=[Position(asset="ETH", free=32.1, locked=0)]),
        [("BTC", 523.1, 32), ("ETH", 32.1, 0)]
    ),
    (
        AccountUpdate(balances=[Position(asset="BTC", free=555.1, locked=0)]),
        [("BTC", 555.1, 0), ("ETH", 32.1, 0)]
    ),
    (
        AccountUpdate(balances=[
            Position(asset="BTC", free=500.1, locked=55.1),
            Position(asset="ETH", free=20, locked=12.1)
        ]), [("BTC", 500.1, 55.1), ("ETH", 20, 12.1)]
    )
]
def test_account_update():
    account = AccountState()

    for test in account_update_cases:
        test[0].handle(account)

        for balance in test[1]:
            (symbol, free, locked) = balance
            assert (free, locked) == account.balance(symbol)


def test_order_update():
    # @todo - we need to really investigate the underlying payload
    #  and exactly what we want to do here.
    pass
