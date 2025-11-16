import cv2
import os
import numpy as np

def detect_lanes(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)

    mask = np.zeros_like(edges)
    h, w = edges.shape
    roi = np.array([[(0, h), (w, h), (w//2, int(h*0.55))]])
    cv2.fillPoly(mask, roi, 255)
    masked = cv2.bitwise_and(edges, mask)

    lines = cv2.HoughLinesP(masked, 1, np.pi/180, threshold=50, minLineLength=50, maxLineGap=150)
    line_img = np.zeros_like(img)

    if lines is not None:
        for l in lines:
            x1, y1, x2, y2 = l[0]
            cv2.line(line_img, (x1, y1), (x2, y2), (0, 255, 0), 3)

    combined = cv2.addWeighted(img, 0.8, line_img, 1, 0)
    return combined


def process_lane_images(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    images = sorted([f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg'))])
    
    if not images:
        print("No images found in folder:", input_folder)
        return

    for img_file in images:
        img_path = os.path.join(input_folder, img_file)
        img = cv2.imread(img_path)
        if img is None:
            continue
        annotated = detect_lanes(img)
        cv2.imwrite(os.path.join(output_folder, img_file), annotated)