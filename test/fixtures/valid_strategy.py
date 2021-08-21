from algorunner.adapters import TransactionRequest
from algorunner.mutations import AccountState
from algorunner.strategy import BaseStrategy


class ValidStrategy(BaseStrategy):
    def process(self, tick):
        return True
    
    def authorise(self, state: AccountState, trx: TransactionRequest) -> TransactionRequest:
        pass
