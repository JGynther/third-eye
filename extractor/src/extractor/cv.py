import cv2
import numpy as np

SCALE_FACTOR = 0.25
INVERSE_SCALE_FACTOR = 1 / SCALE_FACTOR


def crop_card_bbox(image: cv2.typing.MatLike) -> list[cv2.typing.MatLike]:
    resized = cv2.resize(image, (0, 0), fx=SCALE_FACTOR, fy=SCALE_FACTOR)
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    filtered = cv2.bilateralFilter(gray, 9, 75, 75)

    edges = cv2.Canny(filtered, 50, 150)

    kernel = np.ones((3, 3), np.uint8)
    dilated = cv2.dilate(edges, kernel)

    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    cropped_images = []

    for cnt in contours:
        area = cv2.contourArea(cnt)

        if area < 5000:
            continue

        rect = cv2.minAreaRect(cnt)

        _, (w, h), _ = rect

        w *= INVERSE_SCALE_FACTOR
        h *= INVERSE_SCALE_FACTOR
        aspect = min(w, h) / max(w, h)

        if 0.6 > aspect or aspect > 0.85:
            print("skipped", aspect)
            continue

        box = cv2.boxPoints(rect) * INVERSE_SCALE_FACTOR

        m = cv2.getPerspectiveTransform(
            box, np.array([[0, h], [0, 0], [w, 0], [w, h]], dtype=np.float32)
        )

        warped = cv2.warpPerspective(image, m, (int(w), int(h)))
        h, w = warped.shape[:2]

        if w > h:
            warped = cv2.rotate(warped, cv2.ROTATE_90_CLOCKWISE)

        cropped_images.append(warped)

    return cropped_images
