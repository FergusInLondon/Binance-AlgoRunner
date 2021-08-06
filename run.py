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
@click.option('-c', '--config', 'config_file', default='bot.ini', short_help='Configuration file.')
@click.option('-s', '--strategy', 'strategy_name', short_help='Name of Strategy to run')
@click.option('--testing', isflag=True, default=True,  short_help='Run in testing mode, NOT live')
@click.option('--exchange', envvar='ALGORUNNER_EXCHANGE', short_help='Crypto exchange to execute strategy against')
@click.option('--api-key', envvar='ALGORUNNER_API_KEY', short_help='API Key for exchange/broker')
@click.option('--api-secret', envvar='ALGORUNNER_API_SECRET', short_help='API Secret for exchange/broker')
@click.option('--trading-symbol', envvar='ALGORUNNER_TRADING_SYMBOL', short_help='Symbol to execute strategy against')
def entrypoint(
    config_file: str,
    strategy_name: str,
    testing: bool,
    exchange: str,
    apiKey: str,
    apiSecret: str,
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
        apiKey = apiKey if apiKey else cfg['credentials']['api_key']
        apiSecret = apiSecret if apiSecret else cfg['credentials']['api_secret']
        strategy_name = strategy_name if strategy_name else cfg['strategy']['name']
        exchange = exchange if exchange else cfg['credentials']['exchange']
        trading_symbol = trading_symbol if trading_symbol else cfg['credentials']['symbol']
    except KeyError:
        raise exceptions.InvalidConfiguration(exceptions.MSG_MISSING_CONFIG)

    # Filter out any empty config options
    if not all([apiKey, apiSecret, strategy_name, exchange, trading_symbol]):
        raise exceptions.InvalidConfiguration(exceptions.MSG_MISSING_CONFIG)

    strategy = load_strategy(strategy_name)
    runner = Runner(Credentials(
        exchange=exchange,
        key=apiKey,
        secret=apiSecret
    ), trading_symbol, strategy)
    runner.run()


if __name__ == "__main__":
    try:
        entrypoint()
    except exceptions.InvalidConfiguration as e:
        logger.critical("CRITICAL FAILURE: incorrect configuration provided", e.message)
    except exceptions.FailureLoadingStrategy as e:
        logger.critical("CRITICAL FAILURE: unable to instantiate strategy", e.message)
    except exceptions.UnknownExchange as e:
        logger.critical("CRITICAL FAILURE: invalid exchange specified in config", e.message)
    except Exception as e:
        logger.critical("CRITICAL FAILURE: Terminating...", e)
