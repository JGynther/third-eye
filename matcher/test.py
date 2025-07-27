from PIL import Image, ImageFile
from itertools import batched
from pathlib import Path

ImageFile.LOAD_TRUNCATED_IMAGES = True

CACHE = Path(".cache")
IMAGES = CACHE / "images"

for batch in batched(IMAGES.glob("*.jpg"), 128):
    images = [Image.open(path) for path in batch]
