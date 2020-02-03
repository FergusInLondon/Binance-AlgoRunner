
class Account(object):
    """
        The Account is responsible for keeping track of user balances, it's
        updated via a UserSocket.
    """

    can_withdraw = None
    can_trade = None
    can_deposit = None
    balances = {}

    def __init__(self, payload):
        self.can_withdraw = payload["canWithdraw"]
        self.can_trade = payload["canTrade"]
        self.can_deposit = payload["canDeposit"]

        for asset in payload["balances"]:
            self.balances[asset["asset"]] = (
                float(asset["free"]), float(asset["locked"]))

    def __call__(self, payload):
        """
            For simplicity Account is callable.
        """

        action = {
            'outboundAccountInfo': self.account_update,
            'outboundAccountPosition': self.position_update,
            'balanceUpdate': self.balance_update,
            'executionReport': self.order_report
        }.get(payload["e"],
              lambda p: print("unhandled account event ", p["e"]))

        action(payload)

    def account_update(self, payload):
        self.can_withdraw = payload["W"]
        self.can_trade = payload["T"]
        self.can_deposit = payload["D"]

        for asset in payload["B"]:
            self.balances[asset["a"]] = (float(asset["f"]), float(asset["l"]))

    def position_update(self, payload):
        for asset in payload["B"]:
            self.balances[asset["a"]] = (float(asset["f"]), float(asset["l"]))

    def balance_update(self, payload):
        self.balances[payload["a"]] = (
            self.balances[payload["a"]][0] + float(payload["d"]),
            self.balances[payload["a"]][1]
        )

    def order_report(self, payload):
        # Not entirely sure what, if anything other than logging, we should do
        # here. After all, actual account updates/state are already handled.
        pass

    def capability_trade(self):
        return self.can_trade

    def capability_withdraw(self):
        return self.can_withdraw

    def capability_deposit(self):
        return self.can_deposit

    def balance(self, asset):
        return self.balances.get(asset, None)

    def buy(self, asset, amount, limit=False, price=0):
        if limit:
            self.binance.order_limit_buy(
                symbol=asset,
                quantity=amount,
                price=price)
        else:
            self.binance.order_market_buy(
                symbol=asset,
                quantity=amount)

    def sell(self, asset, amount, limit=False, price=0):
        if limit:
            self.binance.order_limit_sell(
                symbol=asset,
                quantity=amount,
                price=price)
        else:
            self.binance.order_market_sell(
                symbol=asset,
                quantity=amount)
