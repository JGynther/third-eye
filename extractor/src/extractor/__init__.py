from pathlib import Path
from uuid import uuid4

from cv2 import imread, imwrite

from .cv import crop_card_bbox

TMP = Path(".tmp")
TMP.mkdir(exist_ok=True)


def find_all_cards_from(image: str):
    original = imread(image)

    ids: list[str] = []

    for img in crop_card_bbox(original):
        id = str(TMP / f"{uuid4()}.jpg")
        imwrite(id, img)
        ids.append(id)

    return ids
