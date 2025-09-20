import cv2
import numpy as np
import os
from skimage.filters import threshold_otsu
import glob

def adjust_local_brightness_contrast(image):
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    cl = clahe.apply(l)
    limg = cv2.merge((cl, a, b))
    adjusted = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    return adjusted

def adjust_for_dark_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    mean_intensity = np.mean(gray)
    if mean_intensity < 80:  # Very dark image threshold
        # Apply gamma correction to brighten
        gamma = 1.8  # increase brightness for dark image
        invGamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** invGamma) * 255
                          for i in np.arange(256)]).astype("uint8")
        brightened = cv2.LUT(image, table)
        return brightened
    return image

def get_bubble_contours(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    adjusted = gray if np.mean(gray) > 100 else cv2.cvtColor(adjust_local_brightness_contrast(image), cv2.COLOR_BGR2GRAY)

    thresh_val = threshold_otsu(adjusted)
    _, binary = cv2.threshold(adjusted, thresh_val-15, 255, cv2.THRESH_BINARY_INV)

    kernel = np.ones((5,5), np.uint8)
    opening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(opening, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    bubble_contours = []

    for cnt in contours:
        area = cv2.contourArea(cnt)
        perimeter = cv2.arcLength(cnt, True)
        if 120 < area < 2500 and perimeter > 25:  # relaxed thresholds
            approx = cv2.approxPolyDP(cnt, 0.02*perimeter, True)
            if len(approx) > 5:
                circularity = (4 * np.pi * area) / (perimeter * perimeter)
                if 0.7 < circularity < 1.2:
                    hull = cv2.convexHull(cnt)
                    hull_area = cv2.contourArea(hull)
                    solidity = area / hull_area if hull_area > 0 else 0
                    if solidity > 0.85:
                        bubble_contours.append(cnt)
    return bubble_contours

def analyze_fill_level(image_gray, contour):
    mask = np.zeros(image_gray.shape, dtype=np.uint8)
    cv2.drawContours(mask, [contour], -1, 255, -1)
    mean_val = cv2.mean(image_gray, mask=mask)[0]
    return mean_val

def highlight_filled_bubbles(image, bubble_contours, fill_threshold=150):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    highlighted = image.copy()
    for cnt in bubble_contours:
        fill_level = analyze_fill_level(gray, cnt)
        if fill_level < fill_threshold:  # increased threshold to capture light fill
            mask = np.zeros(gray.shape, dtype=np.uint8)
            cv2.drawContours(mask, [cnt], -1, 255, -1)
            filled_pixels = cv2.countNonZero(cv2.bitwise_and(mask, cv2.inRange(gray, 0, fill_threshold)))
            total_pixels = cv2.countNonZero(mask)
            fill_ratio = filled_pixels / total_pixels if total_pixels > 0 else 0
            if fill_ratio > 0.35:  # allow partial fill detection
                cv2.drawContours(highlighted, [cnt], -1, (0, 255, 0), 2)
    return highlighted

def process_image(input_path, output_path):
    image = cv2.imread(input_path)
    if image is None:
        print(f"Failed to load {input_path}")
        return

    # Step 1: Brighten if extremely dark
    image = adjust_for_dark_image(image)

    # Step 2: Apply local brightness/contrast adjustment
    enhanced_image = adjust_local_brightness_contrast(image)

    # Step 3: Detect bubbles
    bubbles = get_bubble_contours(enhanced_image)

    # Step 4: Highlight filled bubbles
    highlighted_img = highlight_filled_bubbles(enhanced_image, bubbles)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv2.imwrite(output_path, highlighted_img)

def batch_process_images(input_dir='data/input', output_dir='data/output'):
    for set_folder in os.listdir(input_dir):
        set_path = os.path.join(input_dir, set_folder)
        if os.path.isdir(set_path):
            for image_file in glob.glob(os.path.join(set_path, '*.jpeg')):
                rel_path = os.path.relpath(image_file, input_dir)
                output_path = os.path.join(output_dir, rel_path)
                process_image(image_file, output_path)

batch_process_images()
