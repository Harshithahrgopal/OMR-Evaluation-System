import cv2
import numpy as np

def detect_bubbles(sheet_img):
    gray = cv2.cvtColor(sheet_img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    bubbles = []
    for c in contours:
        area = cv2.contourArea(c)
        perimeter = cv2.arcLength(c, True)
        if perimeter == 0:
            continue
        circularity = 4*np.pi*area/(perimeter**2)
        if 0.7 < circularity < 1.2 and 10 < area < 2000:  # adjust area based on sheet
            x, y, w, h = cv2.boundingRect(c)
            crop = thresh[y:y+h, x:x+w]
            crop = cv2.resize(crop, (28,28))
            bubbles.append((x, y, crop))
    
    # Sort by y then x
    bubbles.sort(key=lambda b: (b[1], b[0]))
    return bubbles
