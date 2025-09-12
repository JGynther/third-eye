from itertools import batched

import faiss
import numpy as np
from httpx import AsyncClient
from tqdm import tqdm

from .paths import IDS, IMAGES, INDEX

BATCH_SIZE = 128


async def get_embeddings(paths: list[str]) -> np.typing.NDArray[np.float32]:
    async with AsyncClient() as client:
        result = await client.post(
            "http://localhost:8000/embed",
            json=paths,
            timeout=60,
        )

    result.raise_for_status()
    json = result.json()

    return np.array(json, dtype=np.float32)


def create_index():
    index = faiss.IndexFlatL2(384)  # 768, 1152

    with IDS.open("w") as f:
        for batch in tqdm(batched(IMAGES.glob("*.jpg"), BATCH_SIZE)):
            paths = [str(path) for path in batch]
            embeddings = get_embeddings(paths)
            index.add(embeddings)  # type: ignore

            for path in batch:
                f.write(f"{path.stem}\n")

    faiss.write_index(index, str(INDEX))
