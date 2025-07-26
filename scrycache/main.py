import asyncio
import json
import typing as T
from pathlib import Path

import httpx

SCRYFALL_BULK_URI = "https://api.scryfall.com/bulk-data"

CACHE = Path(".cache")
CARDS = CACHE / "cards.json"
IMAGES = CACHE / "images"

CACHE.mkdir(exist_ok=True)
IMAGES.mkdir(exist_ok=True)


def download_bulk_data():
    response = httpx.get(SCRYFALL_BULK_URI, timeout=60)
    response.raise_for_status()

    for each in response.json().get("data"):
        if not each["type"] == "default_cards":
            continue

        data = httpx.get(each["download_uri"])
        data.raise_for_status()

        CARDS.write_bytes(data.content)


class ImageUris(T.TypedDict):
    normal: str


class Face(T.TypedDict):
    image_uris: T.NotRequired[ImageUris]


class Card(T.TypedDict):
    id: str
    image_uris: T.NotRequired[ImageUris]
    card_faces: T.NotRequired[list[Face]]


class Downloadable(T.NamedTuple):
    id: str
    uri: str
    path: Path


def downloadable(card: Card) -> list[Downloadable]:
    id = card["id"]

    match card:
        case {"image_uris": {"normal": uri}}:
            return [Downloadable(id, uri, IMAGES / f"{id}.jpg")]

        case {"card_faces": [front, back]}:
            match front, back:
                case {
                    "image_uris": {
                        "normal": front_uri,
                    },
                }, {
                    "image_uris": {
                        "normal": back_uri,
                    },
                }:
                    return [
                        Downloadable(
                            f"{id}_1",
                            front_uri,
                            IMAGES / f"{id}_1.jpg",
                        ),
                        Downloadable(
                            f"{id}_2",
                            back_uri,
                            IMAGES / f"{id}_2.jpg",
                        ),
                    ]

                case _:
                    return []

        case _:
            return []


async def download_image(
    semaphore: asyncio.Semaphore,
    client: httpx.AsyncClient,
    id: str,
    uri: str,
    path: Path,
) -> bool:
    async with semaphore:
        try:
            response = await client.get(uri)
            response.raise_for_status()

            await asyncio.to_thread(path.write_bytes, response.content)
            print(f"✓ Downloaded {id}")

            return True

        except Exception as error:
            print(f"✗ Failed {id}: {error}")

            return False


async def main():
    if not CARDS.exists():
        download_bulk_data()

    cards: list[Card] = json.loads(CARDS.read_bytes())

    to_download: list[Downloadable] = []

    for card in cards:
        for image in downloadable(card):
            if not image.path.exists():
                to_download.append(image)

    semaphore = asyncio.Semaphore(100)

    async with httpx.AsyncClient() as client:
        async with asyncio.TaskGroup() as tg:
            tasks = [
                tg.create_task(download_image(semaphore, client, id, uri, path))
                for id, uri, path in to_download
            ]

    success = 0

    for task in tasks:
        if task.result():
            success += 1

    print(f"✓ Downloaded {success}/{len(to_download)} images")


if __name__ == "__main__":
    asyncio.run(main())
