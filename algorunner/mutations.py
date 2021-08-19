from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Tuple

from loguru import logger

from algorunner.exceptions import NoBalanceAvailable, InvalidUpdate


class AccountState:
    """Stores a snapshot of the state of the account linked to the current exchange."""

    def __init__(self):
        self.balances = {}
        self.orders = {}
        self.permissions = {
            # assume true - as most likely case - until updated otherwise.
            "can_withdraw": True,
            "can_deposit": True,
            "can_trade": True,
        }

    def balance(self, asset: str) -> Tuple[float, float]:
        balance = self.balances.get(asset)
        if not balance:
            raise NoBalanceAvailable(asset)

        return (balance.free, balance.locked)

    def capability(self, capability: str) -> bool:
        return self.permissions.get(capability, False)


class BaseUpdate(ABC):
    """BaseUpdate defines the interface an Update must adhere to."""

    REQUIRED_PROPS = []

    def __init__(self, **kwargs):
        for prop in self.REQUIRED_PROPS:
            if prop not in kwargs:
                logger.error(
                    "invalid arguments supplied to update object!",
                    {"expected": self.REQUIRED_PROPS, "actual": kwargs},
                )
                raise InvalidUpdate(prop, self.__class__)

        self.__dict__.update(kwargs)

    @abstractmethod
    def handle(self, state: AccountState) -> AccountState:
        pass


@dataclass
class Position:
    """Position signifies the position associated with a given asset."""

    asset: str
    free: float
    locked: float


_available_updates = set()


def register_update(cls):
    _available_updates.add(cls)
    return cls


def is_update(cls):
    return cls in _available_updates


@register_update
class OrderUpdate(BaseUpdate):
    """Recieved when there are changes to an order associated with the account."""

    REQUIRED_PROPS = ["symbol", "orderId", "side", "type", "status", "quantity"]

    def handle(self, state: AccountState) -> AccountState:
        logger.info("recieved inbound update for pending transaction")
        order = state.orders.get(self.order_id, {})
        # @todo use the | operator when Py 3.9 is fixed.
        state.orders[self.order_id] = {
            **order,
            **{
                "symbol": self.symbol,
                "side": self.side,
                "type": self.type,
                "status": self.status,
                "quantity": self.quantity,
            },
        }
        return state


@register_update
class BalanceUpdate(BaseUpdate):
    """An update containing an individual balance that has changed,
    expressed as delta between balances."""

    REQUIRED_PROPS = ["asset", "delta"]

    def handle(self, state: AccountState) -> AccountState:
        logger.info(f"recieved inbound balance update for '{self.asset}'")
        asset_balance = state.balances.get(
            self.asset, Position(asset=self.asset, free=0, locked=0)
        )

        asset_balance.free += self.delta
        state.balances[self.asset] = asset_balance
        return state


@register_update
class AccountUpdate(BaseUpdate):
    """An update containing any balances which have changed."""

    REQUIRED_PROPS = ["balances"]  # List[Position]

    def handle(self, state: AccountState) -> AccountState:
        logger.info("recieved inbound user update")
        for p in self.balances:
            state.balances[p.asset] = p

        return state


@register_update
class CapabilitiesUpdate(BaseUpdate):
    """The first update an account will recieve upon initialisation."""

    REQUIRED_PROPS = ["can_withdraw", "can_trade", "can_deposit", "positions"]

    def handle(self, state: AccountState) -> AccountState:
        logger.info("recieved inbound capabilities update for current user")
        state.permissions["can_withdraw"] = self.can_withdraw
        state.permissions["can_trade"] = self.can_trade
        state.permissions["can_deposit"] = self.can_deposit

        position_update = AccountUpdate(balances=self.positions)
        return position_update.handle(state)
