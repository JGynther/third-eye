import cv2
import numpy as np

SCALE_FACTOR = 0.25
INVERSE_SCALE_FACTOR = 1 / SCALE_FACTOR


def crop_card_bbox(image: cv2.typing.MatLike) -> list[cv2.typing.MatLike]:
    resized = cv2.resize(image, (0, 0), fx=SCALE_FACTOR, fy=SCALE_FACTOR)
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    filtered = cv2.bilateralFilter(gray, 9, 75, 75)

    edges = cv2.Canny(filtered, 50, 150)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    dilated = cv2.dilate(edges, kernel, iterations=2)

    cv2.imshow("Dilated", dilated)
    cv2.waitKey(0)

    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    cropped_images = []

    for cnt in contours:
        if cv2.contourArea(cnt) < 5000:
            continue

        epsilon = 0.02 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)

        hull = cv2.convexHull(approx)
        box = hull.reshape(-1, 2) * INVERSE_SCALE_FACTOR
        box = order_points(box)

        _, _, w, h = cv2.boundingRect(box)
        aspect = w / (h or 1)

        if 0.6 > aspect or aspect > 0.85:
            print("skipped aspect", aspect)
            continue

        m = cv2.getPerspectiveTransform(
            box,
            np.array(
                [
                    [0, 0],
                    [488 - 1, 0],
                    [488 - 1, 680 - 1],
                    [0, 680 - 1],
                ],
                dtype=np.float32,
            ),
        )

        warped = cv2.warpPerspective(image, m, (488, 680))
        corrected = white_balance_correction(warped)
        cropped_images.append(corrected)

    for cropped in cropped_images:
        cv2.imshow("1", cropped)
        cv2.waitKey(0)

    return cropped_images


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


def white_balance_correction(image: np.ndarray) -> np.ndarray:
    image = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

    avg_a = np.mean(image[:, :, 1])
    avg_b = np.mean(image[:, :, 2])

    image[:, :, 1] = image[:, :, 1] - ((avg_a - 128) * (image[:, :, 0] / 255.0) * 1.1)
    image[:, :, 2] = image[:, :, 2] - ((avg_b - 128) * (image[:, :, 0] / 255.0) * 1.1)

    return cv2.cvtColor(image, cv2.COLOR_LAB2BGR)
