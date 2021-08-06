from enum import Enum
from typing import (
    Dict, NamedTuple, TypedDict, Union
)


class MessageBuyOrder():
    pass


class MessageSellOrder():
    pass


class MessageBalanceUpdate():
    pass


class MessageAccountUpdate():
    pass


class MessagePositionUpdate():
    pass


class MessageOrderUpdate():
    pass


class MessageType(Enum):
    REQUEST_BUY = 1
    REQUEST_SELL = 2
    UPDATE_BALANCE = 3
    UPDATE_ACCOUNT = 4
    UPDATE_POSITION = 5
    UPDATE_ORDER = 6


Message = Union[
    MessageBuyOrder,
    MessageSellOrder,
    MessageBalanceUpdate,
    MessageAccountUpdate,
    MessagePositionUpdate,
    MessageOrderUpdate
]


class TraderMessage(NamedTuple):
    Type: MessageType
    Msg: Message


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


class CalculationResult(Enum):
    """ """
    INSUFFICIENT_FUNDS = 1
    TRANSACTION_REJECTED = 2
    POSITION_UPDATED = 3
    SUCCESSFUL_REBALANCE = 4
