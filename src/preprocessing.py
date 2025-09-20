import cv2
import numpy as np

def preprocess_sheet(img_path, output_size=(2480, 3508)):
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5,5), 0)
    
    # Adaptive threshold
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)
    
    # Find contours and largest rectangle (sheet)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    largest = max(contours, key=cv2.contourArea)
    peri = cv2.arcLength(largest, True)
    approx = cv2.approxPolyDP(largest, 0.02*peri, True)
    
    if len(approx) == 4:
        pts1 = np.float32([p[0] for p in approx])
        pts2 = np.float32([[0,0],[output_size[0],0],[output_size[0],output_size[1]],[0,output_size[1]]])
        M = cv2.getPerspectiveTransform(pts1, pts2)
        warped = cv2.warpPerspective(img, M, output_size)
    else:
        warped = img
    
    return warped
