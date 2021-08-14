from queue import Queue
from unittest import mock
from time import sleep

from behave import *

from algorunner.abstract.base_strategy import (
    ShutdownRequest, BaseStrategy
)
from algorunner.adapters.base import Adapter, OrderType, TransactionRequest
from algorunner.mutations import (
    Position, BalanceUpdate, AccountUpdate, CapabilitiesUpdate
)


@given("a running sync agent awaiting messages")
def new_running_sync_agent(context):
    Adapter.__abstractmethods__ = {}

    context.agent_params = {
        "queue": Queue(),
        "adapter": mock.MagicMock(),
        "auth": mock.MagicMock()
    }

    context.message_list = []
    context.agent = BaseStrategy.SyncAgent(**context.agent_params)
    context.agent.start()
    assert context.agent.is_running()

@when("the sync agent is stopped")
def stop_sync_agent(context):
    context.agent_params["queue"].put(ShutdownRequest(reason="bdd tests"))
    sleep(.25)

@then("it should no longer be running")
def sync_agent_not_running(context):
    assert not context.agent.is_running()

@given("an account update with {capabilities} capabilities")
def account_update_full_capabilities(context, capabilities):
    hasPermission = (capabilities == "full") # todo - just a straight payload swap
    context.message_list.append(CapabilitiesUpdate(
        can_withdraw=hasPermission, can_trade=hasPermission, can_deposit=hasPermission,
        positions=[]
    ))

@when("all messages are processed")
def account_update_processed(context):
    for msg in context.message_list:
        context.agent_params["queue"].put(msg)

    sleep(.5)
    context.message_list = []

@then("the account should have {capabilities} capabilities")
def account_has_full_capabilities(context, capabilities):
    hasPermission = (capabilities == "full")
    for perm in ['can_withdraw', 'can_deposit', 'can_trade']:
        assert context.agent.state.capability(perm) == hasPermission

@given("a {symbol} balance of {free:d} free and {locked:d} locked")
def current_balance(context, symbol, free, locked):
    context.agent.state.balances[symbol] = Position(symbol, free=free, locked=locked)

@given("a balance update of {quantity:g} {symbol}")
def balance_update(context, quantity, symbol):
    context.message_list.append(BalanceUpdate(
        asset=symbol, delta=quantity
    ))

@then("the account should have a balance of {balance:d} {symbol} free")
def balance_for_symbol(context, balance, symbol):
    (free, _) = context.agent.state.balance(symbol)
    assert free == balance

@given("an account position of {symbol} at {free:d} free and {locked:d} locked")
def account_with_balance(context, symbol, free, locked):
    context.agent.state.balances[symbol] = Position(symbol, free=free, locked=locked)

@given("a position update of {symbol} at {free:d} free and {locked:d} locked")
def position_update(context, symbol, free, locked):
    context.message_list.append(AccountUpdate(
        balances=[Position(symbol, free=free, locked=locked)]
    ))

@then("there should be a {symbol} balance of {free:d} free and {locked:d} locked")
def check_symbol_balance(context, symbol, free, locked):
    (_free, _locked) = context.agent.state.balance(symbol)
    assert free == _free
    assert locked == _locked

@then("there should be a total of {count:d} balances")
def check_balance_count(context, count):
    assert len(context.agent.state.balances.keys()) == count

@given("a request to buy {symbol}")
def market_order(context, symbol):
    context.message_list.append(TransactionRequest(
        reason="", symbol="", quantity="", price="", order_type=OrderType.MARKET_SELL
    ))

@given("the order is declined")
def calculator_rejection(context):
    context.agent_params["auth"].return_value = TransactionRequest(
        approved=False, reason="", symbol="", quantity="", price="", order_type=OrderType.MARKET_SELL
    )
        

@given("the order of {symbol} is accepted with a size of {size:g}")
def calculator_accepted(context, symbol, size):
    context.agent_params["auth"].return_value = TransactionRequest(
        approved=True, reason="", symbol="", quantity="", price="", order_type=OrderType.MARKET_SELL
    )
@then("the API should recieve an order of {quantity:g} {symbol}")
def check_for_order(context, quantity, symbol):
    context.agent_params["adapter"].execute.assert_called_once()
    # @todo adapter not called with trx params matching mock calc return

@then("the API should not recieve any orders")
def check_no_orders_made(context):
    context.agent_params["adapter"].execute.assert_not_called()
