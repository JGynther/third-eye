from .cache import download_with_cache


async def refresh_scryfall_cache():
    await download_with_cache()
