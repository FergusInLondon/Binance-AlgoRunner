from algorunner.abstract import BaseStrategy
from algorunner.abstract.base_strategy import (
    AccountState, TransactionRequest
)
class ValidStrategy(BaseStrategy):
    def process(self, tick):
        return True
    
    def authorise(self, state: AccountState, trx: TransactionRequest) -> TransactionRequest:
        pass
