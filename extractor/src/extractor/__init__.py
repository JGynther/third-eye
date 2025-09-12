from pathlib import Path
from uuid import uuid4

from cv2 import imread, imwrite

from .yolo import crop_card_obbox

TMP = Path(".tmp")
TMP.mkdir(exist_ok=True)


def find_all_cards_from_obbox(image: str, debug=False):
    original = imread(image)

    ids: list[str] = []

    for img in crop_card_obbox(original, debug):
        id = str(TMP / f"{uuid4()}.jpg")
        imwrite(id, img)
        ids.append(id)

    return ids
