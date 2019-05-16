import json
from typing import List

from loguru import logger
from redis import StrictRedis
import rx
from rx.concurrency import ThreadPoolScheduler
import rx.operators as op

from fx_service.config import DATABASE_URL, PULL_INTERVAL_SECONDS
from fx_service.provider import (
    Fx1Forge,
    get_currency_pairs_data,
    save_quotes_to_timescaledb,
)

redis_client = StrictRedis(decode_responses=True)


def get_fx_symbols():
    return redis_client.smembers("fx_symbols")


def get_fx_quotes() -> None:
    logger.info("Getting latest fx quotes...")
    symbols = get_fx_symbols()
    quotes = Fx1Forge.get_quotes(symbols)
    # Save data to timescaledb
    save_quotes_to_timescaledb(quotes)
    logger.info("Latest fx quotes saved to timescaledb.")
    # Save data to redis
    redis_client.set("fx_quotes", json.dumps(quotes))
    logger.info("Latest fx quotes saved to redis.")


scheduler = ThreadPoolScheduler()
rx.timer(0, 60.0, scheduler=scheduler).subscribe_(lambda x: get_fx_quotes())

