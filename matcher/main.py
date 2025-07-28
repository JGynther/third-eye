import json
from itertools import batched
from pathlib import Path

import faiss
import httpx
import numpy as np
from tqdm import tqdm

from extractor import find_all_cards_from
from scrycache import refresh_scryfall_cache

CACHE = Path(".cache")
CARDS = CACHE / "cards.json"
IMAGES = CACHE / "images"
INDEX = CACHE / "cards.faiss"
IDS = CACHE / "ids.txt"


def get_embeddings(paths: list[str]) -> np.typing.NDArray[np.float32]:
    result = httpx.post(
        "http://localhost:8000/embed",
        json=paths,
        timeout=60,
    )

    result.raise_for_status()
    json = result.json()

    return np.array(json, dtype=np.float32)


def create_index():
    index = faiss.IndexFlatL2(768)  # 1152

    with IDS.open("w") as f:
        for batch in tqdm(batched(IMAGES.glob("*.jpg"), 128)):
            paths = [str(path) for path in batch]
            embeddings = get_embeddings(paths)
            index.add(embeddings)  # type: ignore

            for path in batch:
                f.write(f"{path.stem}\n")

    faiss.write_index(index, str(INDEX))


def main():
    # refresh_scryfall_cache()

    if not INDEX.exists():
        create_index()

    index: faiss.IndexFlatL2 = faiss.read_index(str(INDEX))

    with IDS.open() as f:
        ids = f.read().splitlines()

    with CARDS.open() as f:
        cards = json.load(f)

    images = find_all_cards_from("images/IMG_5097.jpeg")
    embeddings = get_embeddings(images)
    scores, indices = index.search(embeddings, k=5)  # type: ignore

    for i, (scores, matches) in enumerate(zip(scores, indices)):
        print("img:", images[i])
        for score, match in zip(scores, matches):
            id = ids[match]
            for card in cards:
                if card["id"] == id:
                    print(score, card["scryfall_uri"])
                    break

        print()

    print("Done")


if __name__ == "__main__":
    main()
