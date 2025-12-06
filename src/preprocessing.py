import cv2
import numpy as np


def preprocess_image(img):
    """
    Input:  BGR image (as loaded by cv2.imread)
    Output: (enhanced_gray, binary_threshold)
    """
    if img is None:
        raise ValueError("preprocess_image received None image")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # moderate denoise
    gray = cv2.fastNlMeansDenoising(gray, h=12)

    # sharpen a bit
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    sharp = cv2.addWeighted(gray, 1.7, blur, -0.7, 0)

    # CLAHE
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(sharp)

    # adaptive threshold
    th = cv2.adaptiveThreshold(
        enhanced, 255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY,
        31, 7
    )

    return enhanced, th
