from typing import Optional, List

MSG_INVALID_CONFIG = "unable to parse all required values from configuration"
MSG_INVALID_CONFIG_W_FIELDS = "unable to parse [{fields}] from configuration"
MSG_UNKNOWN_EXCHANGE = "unable to find adapter for exchange '{name}'"


class InvalidConfiguration(Exception):
    """
    Raised when there's an issue with the provided configuration; either an
    option not being specified, or an option being specified incorrectly.
    """
    def __init__(self, invalid_fields: Optional[List[str]]):
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
