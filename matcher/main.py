from itertools import batched
from pathlib import Path

# Order matters
import torch  # isort: skip
import faiss  # isort: skip

from PIL import Image, ImageFile
from tqdm import tqdm
from transformers import AutoModel, AutoProcessor

ImageFile.LOAD_TRUNCATED_IMAGES = True

MODEL = "google/siglip2-so400m-patch16-naflex"
batch_size = 16

CACHE = Path(".cache")
IMAGES = CACHE / "images"
INDEX = CACHE / "cards.faiss"
IDS = CACHE / "ids.txt"


@torch.no_grad()
def main():
    model = AutoModel.from_pretrained(MODEL, device_map="auto")
    processor = AutoProcessor.from_pretrained(MODEL)

    index = faiss.IndexFlatIP(1152)

    with IDS.open("w") as f:
        for batch in tqdm(batched(IMAGES.glob("*.jpg"), batch_size)):
            images = [Image.open(path) for path in batch]
            inputs = processor(images=images, return_tensors="pt").to(model.device)
            embeddings = model.get_image_features(**inputs).cpu().numpy()
            index.add(embeddings)  # type: ignore

            for path in batch:
                f.write(f"{path.stem}\n")

    faiss.write_index(index, str(INDEX))


if __name__ == "__main__":
    main()
