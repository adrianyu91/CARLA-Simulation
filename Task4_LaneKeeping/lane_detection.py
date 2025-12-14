# lane_detection.py
import cv2
import os
import numpy as np

# ------------------------
# Lane tracking class
# ------------------------
class LaneLine:
    """Tracks a line over multiple frames to smooth lane detection."""
    def __init__(self, buffer_size=7):
        self.buffer_size = buffer_size
        self.buffer = []
        self.detected = False
        self.avg_slope = 0.0
        self.avg_intercept = 0.0

    def add_fit(self, slope, intercept):
        self.buffer.append((slope, intercept))
        if len(self.buffer) > self.buffer_size:
            self.buffer.pop(0)
        slopes, intercepts = zip(*self.buffer)
        self.avg_slope = np.mean(slopes)
        self.avg_intercept = np.mean(intercepts)
        self.detected = True

# Instantiate global trackers for left/right lanes
left_tracker = LaneLine()
right_tracker = LaneLine()

# ------------------------
# Lane detection function
# ------------------------
def detect_lanes(img, return_binary=False):
    h, w, _ = img.shape

    # HLS thresholding
    hls = cv2.cvtColor(img, cv2.COLOR_BGR2HLS)
    l_channel = hls[:, :, 1]
    s_channel = hls[:, :, 2]
    _, l_thresh = cv2.threshold(l_channel, 200, 255, cv2.THRESH_BINARY)
    _, s_thresh = cv2.threshold(s_channel, 90, 255, cv2.THRESH_BINARY)
    color_mask = cv2.bitwise_or(l_thresh, s_thresh)

    # Canny edges
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5),0)
    edges = cv2.Canny(blur, 100, 200)

    # Combine
    combined = cv2.bitwise_or(edges, color_mask)

    # ROI mask
    mask = np.zeros_like(combined)
    roi = np.array([[
        (int(0.2*w), h),
        (int(0.45*w), int(0.65*h)),
        (int(0.55*w), int(0.65*h)),
        (int(0.8*w), h)
    ]])
    cv2.fillPoly(mask, roi, 255)
    masked = cv2.bitwise_and(combined, mask)

    # Hough lines
    lines = cv2.HoughLinesP(masked, 1, np.pi/180, 40, minLineLength=40, maxLineGap=150)
    line_img = np.zeros_like(img)
    binary_lane = np.zeros_like(masked)
    left_lines, right_lines = [], []

    if lines is not None:
        for l in lines:
            x1, y1, x2, y2 = l[0]
            if x2 == x1: continue
            slope = (y2-y1)/(x2-x1)
            if abs(slope) < 0.4: continue
            if slope < 0:
                left_lines.append((x1,y1,x2,y2))
            else:
                right_lines.append((x1,y1,x2,y2))

    # Function to average and track lines
    def draw_tracked(lines, tracker):
        if len(lines) == 0 and not tracker.detected:
            return None
        if len(lines) > 0:
            xs, ys = [], []
            for x1,y1,x2,y2 in lines:
                xs.extend([x1,x2])
                ys.extend([y1,y2])
            poly = np.polyfit(xs, ys, 1)
            tracker.add_fit(poly[0], poly[1])
        if not tracker.detected:
            return None
        slope, intercept = tracker.avg_slope, tracker.avg_intercept
        y1_draw = h
        y2_draw = int(h*0.65)
        if slope == 0: return None
        x1_draw = int((y1_draw - intercept)/slope)
        x2_draw = int((y2_draw - intercept)/slope)
        return x1_draw, y1_draw, x2_draw, y2_draw

    for coords in [draw_tracked(left_lines, left_tracker), draw_tracked(right_lines, right_tracker)]:
        if coords:
            x1,y1,x2,y2 = coords
            cv2.line(line_img, (x1,y1),(x2,y2),(0,255,0),5)
            cv2.line(binary_lane,(x1,y1),(x2,y2),255,5)

    annotated = cv2.addWeighted(img, 0.8, line_img,1,0)
    if return_binary:
        return annotated, binary_lane
    return annotated

# ------------------------
# Lane center estimation
# ------------------------
lane_center_history = []
def estimate_lane_center(binary_lane_img):
    global lane_center_history
    h, w = binary_lane_img.shape
    roi = binary_lane_img[h//2:, :]
    ys, xs = np.where(roi>0)
    if len(xs) < 50: return None
    frame_center = w//2
    left_xs = xs[xs < frame_center]
    right_xs = xs[xs > frame_center]
    if len(left_xs) > 0 and len(right_xs) > 0:
        lane_center = int((np.mean(left_xs) + np.mean(right_xs))/2)
    else:
        lane_center = int(np.mean(xs))
    lane_center_history.append(lane_center)
    if len(lane_center_history) > 5:
        lane_center_history.pop(0)
    return int(np.mean(lane_center_history))

# ------------------------
# Process images folder
# ------------------------
def process_lane_images(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    images = sorted([f for f in os.listdir(input_folder) if f.lower().endswith(('.png','.jpg'))])
    if not images:
        print("No images found in folder:", input_folder)
        return
    for img_file in images:
        img_path = os.path.join(input_folder, img_file)
        img = cv2.imread(img_path)
        if img is None: continue
        annotated = detect_lanes(img)
        cv2.imwrite(os.path.join(output_folder,img_file), annotated)
