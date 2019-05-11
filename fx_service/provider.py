from typing import Dict, List
from databases import Database
import requests_async as requests
from requests_html import HTMLSession
from fx_service.tables import rm_fx_quote
import pendulum
import copy

from fx_service.config import FORGE1_API_KEY


class Fx1Forge:
    api_key = FORGE1_API_KEY
    base_url = "https://forex.1forge.com/1.0.3/"

    @classmethod
    async def market_is_open(cls) -> bool:
        """Checks if forex market is open."""
        url = f"{cls.base_url}market_status?api_key={cls.api_key}"
        resp = await requests.get(url)
        data = resp.json()
        return data["market_is_open"]

    @classmethod
    async def get_symbols(cls) -> List:
        """Get all available forex symbols at 1forge."""
        url = f"{cls.base_url}symbols?&api_key={cls.api_key}"
        resp = await requests.get(url)
        return resp.json()

    @classmethod
    async def get_currencies(cls) -> List:
        """Get all available currency symbols at 1forge."""
        symbols = await cls.get_symbols()
        left_symbols = set([pair[:3] for pair in symbols])
        right_symbols = set([pair[3:] for pair in symbols])
        return list(left_symbols.union(right_symbols))

    @classmethod
    async def get_quotes(cls, symbols: List) -> List[Dict]:
        """Get real time forex rates."""
        symbols_str = ",".join(symbols)
        url = f"{cls.base_url}quotes?pairs={symbols_str}&api_key={cls.api_key}"
        resp = await requests.get(url)
        return resp.json()


async def save_quotes_to_timescaledb(quotes: List[Dict], db: Database) -> None:
    values = []
    data = copy.deepcopy(quotes)
    for quote in data:
        if isinstance(quote["timestamp"], int):
            quote["timestamp"] = pendulum.from_timestamp(quote.pop("timestamp"))
        values.append(quote)
    await db.execute_many(rm_fx_quote.insert(), values)


def get_currency_pairs_data() -> Dict:
    """Get major, minor and exotic currency pairs from tradingview.com.

    Returns:
        [Dict] dict with keys: columns and data
    """
    base_url = "https://www.tradingview.com/markets/currencies"
    session = HTMLSession()
    symbols_data = []
    for pair in ["major", "minor", "exotic"]:
        res = session.get(f"{base_url}/rates-{pair}/")
        symbols = [
            r.attrs["data-symbol"].split(":")[1]
            for r in res.html.find("tr[data-symbol]")
        ]
        data = zip(
            symbols,
            [pair] * len(symbols),
            ["FX"] * len(symbols),
            map(lambda x: 0.01 if "JPY" in x else 0.0001, symbols),
            [True] * len(symbols),
        )
        symbols_data.extend(data)

    return {
        "columns": ["symbol", "rank", "type", "pip_value", "active"],
        "data": symbols_data,
    }
