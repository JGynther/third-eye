import cv2
import numpy as np
from ultralytics import YOLO

model = YOLO("best.pt", task="obb")


def order_points(pts):
    rect = np.zeros((4, 2), dtype=np.float32)

    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)

    rect[0] = pts[np.argmin(s)]  # top-left
    rect[2] = pts[np.argmax(s)]  # bottom-right
    rect[1] = pts[np.argmin(diff)]  # top-right
    rect[3] = pts[np.argmax(diff)]  # bottom-left

    return rect


def crop_card_obbox(image: cv2.typing.MatLike, debug=False):
    # image = preprocess(image)
    crops: list[cv2.typing.MatLike] = []

    for result in model.predict(image):
        for points, conf in zip(result.obb.xyxyxyxy.numpy(), result.obb.conf.numpy()):  # type: ignore
            if conf < 0.90:
                continue

            points = order_points(points)
            center = points.mean(axis=0)
            points = (points - center) / 1.1 + center

            dst = np.array(
                [
                    [0, 0],
                    [488 - 1, 0],
                    [488 - 1, 680 - 1],
                    [0, 680 - 1],
                ],
                dtype=np.float32,
            )

            M = cv2.getPerspectiveTransform(points, dst)
            warped = cv2.warpPerspective(image, M, (488, 680))

            if debug:
                cv2.imshow("Cropped", warped)
                cv2.waitKey(0)

            crops.append(warped)

    return crops
