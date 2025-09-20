from src.preprocessing import preprocess_sheet
from src.bubble_detection import detect_bubbles
import numpy as np
import csv

def evaluate_sheet(img_path, model):
    sheet = preprocess_sheet(img_path)
    bubbles = detect_bubbles(sheet)
    answers = {}
    
    for idx, (x, y, crop) in enumerate(bubbles):
        crop = crop.reshape(1,28,28,1)/255.0
        pred = model.predict(crop)[0][0]
        filled = pred > 0.5
        question_num = idx+1  # map properly based on your sheet layout
        option = filled  # later map to A/B/C/D based on position
        answers[f"Q{question_num}"] = option
    
    # Save to CSV
    csv_file = img_path.split('/')[-1].replace('.jpg','.csv')
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Question', 'OptionFilled'])
        for q, val in answers.items():
            writer.writerow([q, val])
    return answers
