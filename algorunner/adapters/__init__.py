"""

Verification of the functionality of an Adapter should be done in a similar fashion to the
Gherkin specification for the binance adapter.
"""

from algorunner.adapters.messages import *  # noqa: F401, F403
from algorunner.adapters.base import (  # noqa: F401
    Adapter,
    factory,
)
