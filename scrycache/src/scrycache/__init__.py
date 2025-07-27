import asyncio

from .cache import download_with_cache


def refresh_scryfall_cache():
    asyncio.run(download_with_cache())
