import configparser
from logging import getLogger

import click

from algorunner import exceptions
from algorunner.runner import (
    Credentials, Runner
)
from algorunner.strategy import load_strategy


logger = getLogger()


@click.command()
@click.option('-c', '--config', 'config_file', default='bot.ini', help='Configuration file.')
@click.option('-s', '--strategy', 'strategy_name', help='Name of Strategy to run')
@click.option('--testing', is_flag=True, default=True,  help='Run in testing mode, NOT live')
@click.option('--exchange', envvar='ALGORUNNER_EXCHANGE', help='Crypto exchange to execute strategy against')
@click.option('--api-key', envvar='ALGORUNNER_API_KEY', help='API Key for exchange/broker')
@click.option('--api-secret', envvar='ALGORUNNER_API_SECRET', help='API Secret for exchange/broker')
@click.option('--trading-symbol', envvar='ALGORUNNER_TRADING_SYMBOL', help='Symbol to execute strategy against')
def entrypoint(
    config_file: str,
    strategy_name: str,
    testing: bool,
    exchange: str,
    api_key: str,
    api_secret: str,
    trading_symbol: str
):
    """AlgoRunner is a simple runner for executing trading strategies against
    cryptocurrency exchanges, with support for executing backtests. By default
    AlgoRunner will run in BACKTEST mode.

    All configuration can be done through a .INI file, although some parameters
    can be passed as CLI arguments and/or environment variables.

    For full details see https://github.com/fergusinlondon/algorunner
    """

    if not testing:
        logger.warn("WARNING: Running in LIVE trading mode.")

    cfg = configparser.ConfigParser()
    cfg.read(config_file)

    try:
        exchange = exchange if exchange else cfg['credentials']['exchange']
        api_key = api_key if api_key else cfg['credentials']['api_key']
        api_secret = api_secret if api_secret else cfg['credentials']['api_secret']
        strategy_name = strategy_name if strategy_name else cfg['strategy']['name']
        trading_symbol = trading_symbol if trading_symbol else cfg['strategy']['symbol']

        if not all([api_key, api_secret, strategy_name, exchange, trading_symbol]):
            raise KeyError
    except KeyError:
        raise exceptions.InvalidConfiguration()

    strategy = load_strategy(strategy_name, logger)
    runner = Runner(Credentials(
        exchange=exchange,
        key=api_key,
        secret=api_secret
    ), trading_symbol, strategy)
    runner.run()


if __name__ == "__main__":
    try:
        entrypoint()
    except exceptions.InvalidConfiguration as e:
        logger.critical("CRITICAL FAILURE: incorrect configuration provided", e.message)
    except exceptions.UnknownExchange as e:
        logger.critical("CRITICAL FAILURE: invalid exchange specified in config", e.message)
    except Exception as e:
        logger.critical("CRITICAL FAILURE: Terminating...", e)
