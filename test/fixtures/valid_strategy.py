from algorunner.abstract.strategy import Strategy

class ValidStrategy(Strategy):
    def process(self, tick):
        return True
