from typing import Optional, List

MSG_INVALID_CONFIG = "unable to parse all required values from configuration"
MSG_INVALID_CONFIG_W_FIELDS = "unable to parse [{fields}] from configuration"
MSG_UNKNOWN_EXCHANGE = "unable to find adapter for exchange '{name}'"


class InvalidConfiguration(Exception):
    """
    Raised when there's an issue with the provided configuration; either an
    option not being specified, or an option being specified incorrectly.
    """
    def __init__(self, invalid_fields: Optional[List[str]] = None):
        self.message = (
            MSG_INVALID_CONFIG if not invalid_fields
            else MSG_INVALID_CONFIG_W_FIELDS.format(fields=invalid_fields.join(", "))
        )


class UnknownExchange(Exception):
    """
    Raised when the exchange specified in the configuration is unknown.
    """
    def __init__(self, exchange_name: str, exception: Optional[Exception]):
        self.message = MSG_UNKNOWN_EXCHANGE.format(name=exchange_name)
        self.exc = exception


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
        self.message = f"missing '{prop}' in update on update type '{update_type}'"


class FailureLoadingStrategy(Exception):
    """
    Raised when a Strategy cannot be instantiated; this may be down to
    loading the Strategy, or errors that render it unexecutable. Also
    stores the original exception if available.
    """
    def __init__(self, strategy_name: str, exception: Optional[Exception]):
        self.message = "unable to instantiate strategy '{name}'".format(name=strategy_name)
        self.exc = exception


class InvalidStrategyProvided(Exception):
    """Raised when the loaded strategy does no inherit from the base class."""
    pass


class StrategyNotFound(Exception):
    """Raised when the module loader is unable to retrieve the strategy."""
    pass
