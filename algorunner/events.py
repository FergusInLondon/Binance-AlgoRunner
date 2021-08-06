from enum import Enum
from typing import (
    Dict, NamedTuple, TypedDict, Union
)


class UpdateType(Enum):
    """ """
    BALANCE = 1
    ACCOUNT = 2
    POSITION = 3


class Position(NamedTuple):
    """ """
    Free: float
    Locked: float


PositionStatus = Dict[str, Position]


class AccountStatus(TypedDict):
    """ """
    CanWithdraw: bool
    CanTrade: bool
    CanDeposit: bool
    Positions: PositionStatus


class BalanceUpdate(TypedDict):
    """ """
    Asset: str
    Update: float


class AccountEventAction(Enum):
    """ """
    NO_ACTION = 1
    BUY = 2
    SELL = 3


UpdateEvent = Union[AccountStatus, BalanceUpdate, PositionStatus]


class CalculationResult(Enum):
    """ """
    INSUFFICIENT_FUNDS = 1
    TRANSACTION_REJECTED = 2
    POSITION_UPDATED = 3
    SUCCESSFUL_REBALANCE = 4
