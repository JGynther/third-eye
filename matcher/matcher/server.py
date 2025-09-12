import asyncio
import json
import shutil
from contextlib import asynccontextmanager
from uuid import uuid4

import faiss
from fastapi import FastAPI, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse

# from scrycache import refresh_scryfall_cache
from .db import get_session, init_db, insert_match, list_collection, list_sessions
from .index import create_index, get_embeddings
from .paths import CARDS, IDS, INDEX, OBJECTS, TMP
from .yolo import get_bboxes

BATCH_SIZE = 128


@asynccontextmanager
async def lifespan(_: FastAPI):
    # FIXME: handle refresh
    # refresh_scryfall_cache()

    if not INDEX.exists():
        create_index()

    # Prepare SQLite db
    init_db()
    sqlite_write_lock = asyncio.Lock()

    index = faiss.read_index(str(INDEX))
    ids = IDS.read_text().splitlines()

    cards = json.loads(CARDS.read_bytes())
    cards = {card["id"]: card for card in cards}

    yield {
        "index": index,
        "ids": ids,
        "cards": cards,
        "sqlite_write_lock": sqlite_write_lock,
    }

    shutil.rmtree(TMP)


app = FastAPI(lifespan=lifespan)


@app.post("/upload-image")
async def upload(image: UploadFile) -> str:
    id = str(uuid4())

    path = OBJECTS / id
    path.write_bytes(await image.read())

    return id


@app.get("/similar-from-image/{id}")
async def similar(request: Request, id: str):
    index: faiss.IndexFlatL2 = request.state.index
    ids: list[str] = request.state.ids

    path = OBJECTS / id
    images = await get_bboxes(str(path))
    embeddings = await get_embeddings(images)
    scores, indices = index.search(embeddings, k=9)  # type: ignore

    result = []

    for i, (scores, matches) in enumerate(zip(scores, indices)):
        row = {"img": images[i], "matches": []}

        for score, match in zip(scores, matches):
            id = ids[match]

            # handle multifaced ids: _1 or _2 suffix
            if id[-2] == "_":
                id = id[:-2]

            row["matches"].append({"id": id, "score": float(score)})

        result.append(row)

    return result


@app.put("/match")
async def match(request: Request, id: str, src: str, session: str):
    lock: asyncio.Lock = request.state.sqlite_write_lock

    async with lock:
        await asyncio.to_thread(insert_match, id, src, session)


def extract_image_uri(card: dict) -> str:
    if uris := card.get("image_uris"):
        return uris.get("normal", None)

    return card.get("card_faces", [])[0].get("image_uris", {}).get("normal", None)


def usd_to_eur(price: str) -> str:
    return str(float(price) * 0.86)


def extract_price(card: dict) -> str:
    foil = card["foil"]
    nonfoil = card["nonfoil"]
    prices = card["prices"]

    if foil and not nonfoil:
        if price := prices["eur_foil"]:
            return price

        if price := prices["usd_foil"]:
            return usd_to_eur(price)

    if price := prices["eur"]:
        return price

    if price := prices["usd"]:
        return usd_to_eur(price)

    return "0.00"


def cards_by_id(cards: dict, ids: list[str]) -> list[dict]:
    results = []

    for id in ids:
        if card := cards.get(id):
            results.append(
                {
                    "name": card["name"],
                    "link": card["scryfall_uri"],
                    "set": card["set"],
                    "set_name": card["set_name"],
                    "image": extract_image_uri(card),
                    "price": extract_price(card),
                    "edhrec": card.get("edhrec_rank", 0),
                }
            )

    return results


@app.get("/cards")
async def cards(request: Request, ids: list[str] = Query()):
    cards = request.state.cards
    results = cards_by_id(cards, ids)

    if not results:
        raise HTTPException(status_code=404, detail="No cards found")

    return results


@app.get("/session/{id}")
async def session(id: str):
    return await asyncio.to_thread(get_session, id)


@app.get("/sessions")
async def sessions():
    return await asyncio.to_thread(list_sessions)


@app.get("/tmp/images/{image}")
async def tmp(image: str):
    return FileResponse(TMP / image)


@app.get("/collection")
async def collection(
    request: Request,
):
    cards = request.state.cards
    ids = await asyncio.to_thread(list_collection)
    ids = [id for (id,) in ids]

    return cards_by_id(cards, ids)
