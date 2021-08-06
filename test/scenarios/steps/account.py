from behave import *

from algorunner.events import (
    AccountStatus, UpdateType
)
from algorunner.trader import Trader

@given("an account with no initial state")
def fresh_account(context):
    context.trader = Trader()

@given("that account is currently awaiting messages")
def account_running(context):
    pass

@given("an account update with {capabilities} capabilities")
def account_update_full_capabilities(context, capabilities):
    hasPermission = (capabilities == "full")
    context.account_update = AccountStatus(
        CanWithdraw=hasPermission,
        CanTrade=hasPermission,
        CanDeposit=hasPermission
    )

@when("that account update is processed")
def account_update_processed(context):
    context.trader(UpdateType.ACCOUNT, context.account_update)

@then("the account should have {capabilities} capabilities")
def account_has_full_capabilities(context, capabilities):
    hasPermission = (capabilities == "full")
    assert context.trader.status["CanWithdraw"] == hasPermission
    assert context.trader.status["CanTrade"] == hasPermission
    assert context.trader.status["CanDeposit"] == hasPermission

@given("a {symbol} balance of {free} free and {locked} locked")
def current_balance(context, symbol, free, locked):
    pass

@given("a balance update of {quantity:g} {symbol}")
def balance_update(context, quantity, symbol):
    pass

@when("that balance update is processed")
def balance_updated_processed(context):
    pass

@then("the account should have a balance of {balance:d} {symbol} free")
def balance_for_symbol(context, balance, symbol):
    pass

@given("an account position of {symbol} at {free:d} free and {locked:d} locked")
def account_with_balance(context, symbol, free, locked):
    pass

@given("a position update of {symbol} at {free:d} free and {locked:d} locked")
def position_update(context, symbol, free, locked):
    pass

@when("that position update is processed")
def position_update_processed(context):
    pass

@then("there should be a {symbol} balance of {free:d} free and {locked:d} locked")
def check_symbol_balance(context, symbol, free, locked):
    pass

@then("there should be a total of {count:d} balances")
def check_balance_count(context, count):
    pass

@given("a market order to buy {symbol}")
def market_order(context, symbol):
    pass

@given("the calculator will reject the order")
def calculator_rejection(context):
    pass

@given("the calculator will accept the order with a size of {size:g}")
def calculator_accepted(context, size):
    pass

@when("the order event is processed")
def order_event_process(context):
    pass

@then("the API should recieve an order of {quantity:g} {symbol}")
def check_for_order(context, quantity, symbol):
    pass

@then("the API should not recieve any orders")
def check_no_orders_made(context):
    pass
