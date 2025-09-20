import cv2

def sort_contours(cnts, method="left-to-right"):
    reverse = False
    axis = 0
    if method in ["right-to-left", "bottom-to-top"]:
        reverse = True
    if method in ["top-to-bottom", "bottom-to-top"]:
        axis = 1

    bounding_boxes = [cv2.boundingRect(c) for c in cnts]
    cnts, bounding_boxes = zip(*sorted(zip(cnts, bounding_boxes),
                                       key=lambda b: b[1][axis], reverse=reverse))
    return list(cnts)
