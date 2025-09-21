import cv2
import numpy as np
import os
import glob
import pandas as pd

# Subjects and question mapping
subjects = ['Python', 'EDA', 'SQL', 'POWER BI', 'Statistics']
questions_per_subject = 20
options = ['a', 'b', 'c', 'd']

def extract_answers_from_image(image_path):
    """
    Extract answers from a highlighted OMR image.
    """
    image = cv2.imread(image_path)
    if image is None:
        print(f"Failed to load {image_path}")
        return None

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

    # Detect contours of bubbles
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter contours that look like bubbles
    bubble_contours = []
    for c in contours:
        area = cv2.contourArea(c)
        perimeter = cv2.arcLength(c, True)
        if area > 180 and perimeter > 35:
            bubble_contours.append(c)

    # Map bubbles to their centers
    bubble_centers = []
    for c in bubble_contours:
        M = cv2.moments(c)
        if M["m00"] == 0:
            continue
        cx = int(M["m10"]/M["m00"])
        cy = int(M["m01"]/M["m00"])
        bubble_centers.append((cx, cy, c))

    if not bubble_centers:
        return None

    # Sort bubbles top-to-bottom
    bubble_centers.sort(key=lambda x: x[1])

    # Determine approximate column widths
    img_width = image.shape[1]
    col_width = img_width / len(subjects)
    subject_buckets = {subj: [] for subj in subjects}

    for cx, cy, c in bubble_centers:
        col_idx = min(int(cx // col_width), len(subjects)-1)
        subject_buckets[subjects[col_idx]].append((cx, cy, c))

    # Extract answers
    answers_data = {subj: [] for subj in subjects}

    for subj in subjects:
        # Sort bubbles in this column top-to-bottom
        col_bubbles = sorted(subject_buckets[subj], key=lambda x: x[1])
        # Process in groups of 4 (A-D)
        for i in range(0, len(col_bubbles), 4):
            group = col_bubbles[i:i+4]
            group = sorted(group, key=lambda x: x[0])  # left-to-right

            bubbled_options = []
            for idx, (cx, cy, c) in enumerate(group):
                mask = np.zeros(gray.shape, dtype=np.uint8)
                cv2.drawContours(mask, [c], -1, 255, -1)
                filled_pixels = cv2.countNonZero(cv2.bitwise_and(thresh, mask))
                total_pixels = cv2.countNonZero(mask)
                fill_ratio = filled_pixels / total_pixels if total_pixels > 0 else 0
                if fill_ratio > 0.5:  # adjust threshold if needed
                    bubbled_options.append(options[idx])

            if bubbled_options:
                answers_data[subj].append(",".join(bubbled_options))
            else:
                answers_data[subj].append('')

        # Pad to 20 questions if less
        while len(answers_data[subj]) < questions_per_subject:
            answers_data[subj].append('')

    return answers_data

def save_answers_to_csv(answers_data, output_csv_path):
    """
    Save the extracted answers in Table 1 format.
    """
    rows = []
    for i in range(questions_per_subject):
        row = []
        for subj_idx, subj in enumerate(subjects):
            q_num = i + 1 + (subj_idx * questions_per_subject)
            ans = answers_data[subj][i]
            row.append(f"{q_num} - {ans.lower() if ans else ''}".strip())
        rows.append(row)

    df = pd.DataFrame(rows, columns=subjects)
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    df.to_csv(output_csv_path, index=False)
    print(f"Saved CSV to {output_csv_path}")

def process_all_images(input_root='data/output', csv_root='csv_output'):
    for set_folder in os.listdir(input_root):
        set_path = os.path.join(input_root, set_folder)
        if not os.path.isdir(set_path):
            continue
        for img_file in sorted(glob.glob(os.path.join(set_path, '*.jpeg'))):
            answers = extract_answers_from_image(img_file)
            if answers:
                rel_path = os.path.relpath(img_file, input_root)
                csv_folder = os.path.join(csv_root, os.path.dirname(rel_path))
                os.makedirs(csv_folder, exist_ok=True)
                output_csv_path = os.path.join(csv_folder, os.path.splitext(os.path.basename(img_file))[0] + '.csv')
                save_answers_to_csv(answers, output_csv_path)
                print(f"Processed {img_file}")

if __name__ == "__main__":
    process_all_images()
