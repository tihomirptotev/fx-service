import asyncio
import json
from typing import List

import aioredis
from aioredis import Redis
from databases import Database
from mode import Service
from mode.utils.objects import cached_property

from fx_service.config import DATABASE_URL
from fx_service.provider import (
    Fx1Forge,
    get_currency_pairs_data,
    save_quotes_to_timescaledb,
)

loop = asyncio.get_event_loop()


class App(Service):
    db: Database = None
    redis: Redis = None

    async def on_start(self) -> None:
        await self.db.connect()
        try:
            self.redis = await aioredis.create_redis("redis://localhost", loop=loop)
        except Exception as e:
            self.logger.critical("No connection to redis!")
            await self.stop()
        # self.symbols = await Fx1Forge.get_symbols()

    async def on_stop(self) -> None:
        await self.db.disconnect()
        self.logger.info("Connection to timescaledb closed.")

        if self.redis:
            self.redis.close()
            await self.redis.wait_closed()

    @cached_property
    def db(self) -> Database:
        return Database(DATABASE_URL)

    async def get_fx_symbols(self):
        return await self.redis.smembers("fx_symbols", encoding="utf-8")

    @Service.timer(60.0)
    async def get_fx_quotes(self) -> None:
        self.logger.info("Getting latest fx quotes...")
        symbols = await self.get_fx_symbols()
        quotes = await Fx1Forge.get_quotes(symbols)
        # Save data to timescaledb
        await save_quotes_to_timescaledb(quotes, self.db)
        self.logger.info("Latest fx quotes saved to timescaledb.")
        # Save data to redis
        await self.redis.set("fx_quotes", json.dumps(quotes))
        self.logger.info("Latest fx quotes saved to redis.")


if __name__ == "__main__":
    from mode import Worker

    Worker(App(), loglevel="info", daemon=True).execute_from_commandline()
