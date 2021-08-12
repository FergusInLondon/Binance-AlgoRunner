import pytest

from algorunner.strategy import (
    load_strategy,
    StrategyNotFound,
    InvalidStrategyProvided
)

def test_default_strategies_module():
    strategy = load_strategy('Example')
    assert strategy._testing_tag


def test_custom_strategies_module():
    strategy = load_strategy('ValidStrategy', 'test.fixtures.valid_strategy')
    assert strategy.process(None)


@pytest.mark.parametrize("module, strategy, exception", [
    ('Ehe', 'definitely.not.a.real.module', StrategyNotFound),
    ('InvalidStrategy', 'test.fixtures.invalid_strategy', InvalidStrategyProvided),
])
def test_no_strategy_module_availabe(module, strategy, exception):
    correct_exception = False
    try:
        load_strategy(module, strategy)
    except exception:
        correct_exception = True
    
    assert correct_exception
