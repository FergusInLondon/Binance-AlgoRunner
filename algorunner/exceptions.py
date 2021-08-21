"""
Very few - if any - of these are relevant to user-defined strategies; so
are perhaps worthy of *not* including in the `pdoc` docs? Alternatively,
do we import *all* user required objects in to `algorunner/__init__.py`
and coordinate the docs in one place, *and* simplify imports for strategies?
"""
from typing import Optional, List

MSG_INVALID_CONFIG = "unable to parse all required values from configuration"
MSG_INVALID_CONFIG_W_FIELDS = "unable to parse [{fields}] from configuration"


class InvalidConfiguration(Exception):
    """
    Raised when there's an issue with the provided configuration; either an
    option not being specified, or an option being specified incorrectly.
    """

    def __init__(self, invalid_fields: Optional[List[str]] = None):
        self.message = (
            MSG_INVALID_CONFIG
            if not invalid_fields
            else MSG_INVALID_CONFIG_W_FIELDS.format(
                fields=invalid_fields.join(", ")
            )
        )


class NoBalanceAvailable(Exception):
    """
    Triggered when the an attempt to access a balance that does not exist
    occurs.
    """

    def __init__(self, symbol):
        self.message = f"no balance available for '{symbol}'"


class InvalidUpdate(Exception):
    """
    Triggered when an Update is recieved but there's it's missing a required
    property
    """

    def __init__(self, prop: str, update_type: str):
        self.message = (
            f"missing '{prop}' in update on update type '{update_type}'"
        )
