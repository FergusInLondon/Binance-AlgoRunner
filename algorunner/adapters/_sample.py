
from typing import Callable
from algorunner.adapters.base import (
    Adapter,
    register_adapter
)
from algorunner.adapters.messages import (
    Credentials,
    TransactionRequest,
)


@register_adapter
class SampleAdapter(Adapter):

    identifier = "sample"

    def connect(self, creds: Credentials):
        pass

    def monitor_user(self):
        pass

    def run(self, process: Callable, terminated: bool):
        pass

    def execute(self, trx: TransactionRequest) -> bool:
        pass

    def disconnect(self):
        pass
