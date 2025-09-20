import cv2
import numpy as np
from excel_handler import save_results_sectionwise
import os
from datetime import datetime

# Constants
NUM_QUESTIONS = 100
NUM_OPTIONS = 4
COL_FRAC = [0.1, 0.3, 0.5, 0.7, 0.9]  # Five columns
BUBBLE_WIDTH_FRAC = 0.04
FILL_RATIO_THRESHOLD = 0.35

SECTIONS = [
    ("Python", range(1, 21)),
    ("EDA", range(21, 41)),
    ("SQL", range(41, 61)),
    ("POWER BI", range(61, 81)),
    ("Statistics", range(81, 101)),
]

def ensure_dirs(out_base):
    for sub in ["rectified", "enhanced", "excel"]:
        os.makedirs(os.path.join(out_base, sub), exist_ok=True)

def load_image(path):
    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError(f"Cannot load image: {path}")
    return img

def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def detect_document_and_rectify(img, desired_width=1400):
    orig = img.copy()
    h, w = img.shape[:2]
    ratio = max(1.0, w / desired_width)
    small = cv2.resize(img, (int(w / ratio), int(h / ratio)))
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 75, 200)
    cnts, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]
    doc_cnt = None
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
            doc_cnt = approx.reshape(4, 2)
            break
    if doc_cnt is None:
        # No document detected - return original
        return orig
    doc_cnt = doc_cnt * ratio
    rect = order_points(doc_cnt)
    (tl, tr, br, bl) = rect
    width_a = np.linalg.norm(br - bl)
    width_b = np.linalg.norm(tr - tl)
    max_width = max(int(width_a), int(width_b))
    height_a = np.linalg.norm(tr - br)
    height_b = np.linalg.norm(tl - bl)
    max_height = max(int(height_a), int(height_b))
    dst = np.array([[0, 0], [max_width - 1, 0], 
                   [max_width - 1, max_height - 1], [0, max_height - 1]], dtype="float32")
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(orig, M, (max_width, max_height))
    return warped

def detect_bubbles(rectified):
    results = {}
    h, w = rectified.shape[:2]
    row_height = h // 20  # rows per column
    bubble_w = int(w * BUBBLE_WIDTH_FRAC)
    col_positions = [int(w*f) for f in COL_FRAC]

    gray = cv2.cvtColor(rectified, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    question_number = 1
    for col_idx, x in enumerate(col_positions):
        for row in range(20):
            y_top = row * row_height
            y_bottom = (row+1) * row_height
            row_roi = thresh[y_top:y_bottom, :]
            answered = []
            for i, xpos in enumerate(col_positions):
                x_start = xpos - bubble_w//2
                x_end = xpos + bubble_w//2
                x_start = max(0, x_start)
                x_end = min(row_roi.shape[1], x_end)
                roi = row_roi[:, x_start:x_end]
                if roi.size == 0:
                    continue
                fill_ratio = cv2.countNonZero(roi) / (roi.shape[0] * roi.shape[1])
                if fill_ratio > FILL_RATIO_THRESHOLD:
                    answered.append(chr(97 + i))  # a,b,c,d
            results[question_number] = answered
            question_number += 1
    return results


def increase_brightness_if_needed(img, v_thresh=100):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    v = hsv[:, :, 2]
    mean_v = float(np.mean(v))
    if mean_v >= v_thresh:
        return img
    factor = min(2.0, (v_thresh / max(1.0, mean_v)))
    hsv[:, :, 2] = np.clip(hsv[:, :, 2] * factor + 10, 0, 255).astype(np.uint8)
    enhanced = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return enhanced

def evaluate_omr(image_path, out_base):
    ensure_dirs(out_base)
    img = load_image(image_path)
    rectified = detect_document_and_rectify(img)
    enhanced = increase_brightness_if_needed(rectified)
    results = detect_bubbles(enhanced)
    saved_paths = save_results_sectionwise(results, out_base, image_path, SECTIONS)
    return saved_paths
