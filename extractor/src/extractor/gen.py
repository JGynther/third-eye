import random
from pathlib import Path

import cv2
import numpy as np

from extractor.cv import SCALE_FACTOR

# random.seed(42)


BACKGROUNDS = Path("images/unsplash_background_textures")
CACHE = Path.home() / ".cache/third-eye"
IMAGES = CACHE / "images"

card_images = list(sorted(IMAGES.glob("*.jpg")))
backgrounds = list(sorted(BACKGROUNDS.glob("*.jpg")))


def rotate(img: cv2.typing.MatLike, angle: float):
    (h, w) = img.shape[:2]
    (center_x, center_y) = (w / 2, h / 2)

    # Compute rotation matrix
    M = cv2.getRotationMatrix2D((center_x, center_y), angle, 1.0)

    # Compute the new bounding dimensions
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])

    new_w = int((h * sin) + (w * cos))
    new_h = int((h * cos) + (w * sin))

    # Adjust the rotation matrix to account for translation
    M[0, 2] += (new_w / 2) - center_x
    M[1, 2] += (new_h / 2) - center_y

    # Perform the rotation without cropping
    rotated_img = cv2.warpAffine(
        img,
        M,
        (new_w, new_h),
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(255, 0, 255),
    )

    return rotated_img, M


def order_points(pts):
    # Order points clockwise starting from top-left
    rect = np.zeros((4, 2), dtype=np.float32)

    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)

    rect[0] = pts[np.argmin(s)]  # top-left
    rect[2] = pts[np.argmax(s)]  # bottom-right
    rect[1] = pts[np.argmin(diff)]  # top-right
    rect[3] = pts[np.argmax(diff)]  # bottom-left

    return rect


def calculate_corners(h, w, M: None | cv2.typing.MatLike):
    corners = np.array([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]])

    if M is None:
        return corners

    points = corners.reshape(-1, 1, 2)
    transformed = cv2.transform(points, M)
    transformed_corners = transformed.reshape(-1, 2)

    return order_points(transformed_corners)


def random_transform_card(img: cv2.typing.MatLike):
    h, w = img.shape[:2]
    M = None

    if random.random() < 0.5:
        angle = random.uniform(-30, 30)
        img, M = rotate(img, angle)

    if random.random() < 0.3:
        kernel_size = random.choice([3, 5, 7, 9])
        img = cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)

    return img, calculate_corners(h, w, M)


def overlay(bg, img, x, y):
    h, w = img.shape[:2]
    roi = bg[y : y + h, x : x + w]

    lower = np.array([240, 0, 240])
    upper = np.array([255, 15, 255])
    mask = cv2.inRange(img, lower, upper)
    mask_inv = cv2.bitwise_not(mask)

    bg_part = cv2.bitwise_and(roi, roi, mask=mask)
    card_part = cv2.bitwise_and(img, img, mask=mask_inv)

    dst = cv2.add(bg_part, card_part)
    bg[y : y + h, x : x + w] = dst
    return bg


def save_yolo_obb(label: Path, corners):
    with open(label, "a") as f:
        coordinates = " ".join(f"{x:.6f} {y:.6f}" for x, y in corners)
        f.write(f"0 {coordinates}\n")


INTERMEDIATE_SIZE = 2000
TARGET_SIZE = 640
SCALE_FACTOR = TARGET_SIZE / INTERMEDIATE_SIZE


def make_image(label: Path, image: Path, debug=False):
    bg = cv2.imread(str(random.choice(backgrounds)))
    bg = cv2.resize(bg, (INTERMEDIATE_SIZE, INTERMEDIATE_SIZE))

    for _ in range(random.randint(1, 6)):
        img = cv2.imread(str(random.choice(card_images)))
        img, corners = random_transform_card(img)

        bg_h, bg_w = bg.shape[:2]
        card_h, card_w = img.shape[:2]

        margin = 20
        x = random.randint(margin, bg_w - card_w - margin)
        y = random.randint(margin, bg_h - card_h - margin)

        overlay(bg, img, x, y)

        corners = (corners + np.array([x, y])) * SCALE_FACTOR / TARGET_SIZE
        save_yolo_obb(label, corners)

        if debug:
            for index, (cx, cy) in enumerate(corners):
                cx = cx * TARGET_SIZE / SCALE_FACTOR
                cy = cy * TARGET_SIZE / SCALE_FACTOR

                cv2.circle(bg, (int(cx), int(cy)), 15, (0, 0, 255), -1)
                cv2.putText(
                    bg,
                    str(index),
                    (int(cx) + 10, int(cy) + 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    3,
                    (0, 255, 0),
                    4,
                )

    bg = cv2.resize(bg, (TARGET_SIZE, TARGET_SIZE))

    if debug:
        cv2.imshow("Final", bg)
        cv2.waitKey(0)

    else:
        cv2.imwrite(str(image), bg)


def gen_images():
    DATA = Path("dataset")

    LABELS = DATA / "labels"
    IMAGES = DATA / "images"

    LABELS_TRAIN = LABELS / "train"
    LABELS_VAL = LABELS / "val"

    IMAGES_TRAIN = IMAGES / "train"
    IMAGES_VAL = IMAGES / "val"

    LABELS_TRAIN.mkdir(parents=True, exist_ok=True)
    LABELS_VAL.mkdir(parents=True, exist_ok=True)
    IMAGES_TRAIN.mkdir(parents=True, exist_ok=True)
    IMAGES_VAL.mkdir(parents=True, exist_ok=True)

    for index in range(1, 11):
        label = LABELS_TRAIN / f"{index:05d}.txt"
        image = IMAGES_TRAIN / f"{index:05d}.jpg"
        make_image(label, image, debug=True)

    # for index in range(1, 51):
    #    label = LABELS_VAL / f"{index:05d}.txt"
    #    image = IMAGES_VAL / f"{index:05d}.jpg"
    #    make_image(label, image, debug=True)


gen_images()
