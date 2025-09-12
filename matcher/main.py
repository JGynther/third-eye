import asyncio
import json

import faiss

from matcher.index import get_embeddings
from matcher.paths import CARDS, IDS, INDEX
from matcher.yolo import get_bboxes


def run_with_debug(img: str):
    index = faiss.read_index(str(INDEX))
    ids = IDS.read_text().splitlines()

    cards = json.loads(CARDS.read_bytes())
    cards = {card["id"]: card for card in cards}

    images = asyncio.run(get_bboxes(img), debug=True)
    embeddings = asyncio.run(get_embeddings(images))
    scores, indices = index.search(embeddings, k=6)  # type: ignore

    for scores, matches in zip(scores, indices):
        score = scores[0]
        match = matches[0]

        # handle multifaced ids: _1 or _2 suffix
        id = ids[match]
        if id[-2] == "_":
            id = id[:-2]

        card = cards[id]

        print(score, card["scryfall_uri"])


if __name__ == "__main__":
    for img in [
        "images/IMG_5183.jpeg",
        # "images/IMG_5092.jpeg",
        # "images/IMG_5175.jpeg",
        # "images/IMG_5103.jpeg",
        # "images/IMG_5102.jpeg",
    ]:
        run_with_debug(img)
        print("\n\n\n")
