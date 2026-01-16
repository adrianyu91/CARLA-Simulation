# lane_detection.py
import cv2
import os
import numpy as np

# ------------------------
# Lane tracking class
# ------------------------
class LaneLine:
    """Tracks a line over multiple frames to smooth lane detection."""
    def __init__(self, buffer_size=10):
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

def reset_trackers():
    """Reset lane trackers when detection fails."""
    global left_tracker, right_tracker
    left_tracker = LaneLine()
    right_tracker = LaneLine()

# Instantiate global trackers for left/right lanes
left_tracker = LaneLine()
right_tracker = LaneLine()

# ------------------------
# Lane detection function
# ------------------------
def detect_lanes(img, return_binary=False):
    global left_tracker, right_tracker
    h, w, _ = img.shape

    # HLS thresholding
    hls = cv2.cvtColor(img, cv2.COLOR_BGR2HLS)
    l_channel = hls[:, :, 1]
    s_channel = hls[:, :, 2]
    _, l_thresh = cv2.threshold(l_channel, 190, 255, cv2.THRESH_BINARY) # was 200
    _, s_thresh = cv2.threshold(s_channel, 85, 255, cv2.THRESH_BINARY) # was 90
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
        (int(0.15*w), h), # was 0.2
        (int(0.45*w), int(0.65*h)),
        (int(0.55*w), int(0.65*h)),
        (int(0.85*w), h) # was 0.8
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
    
    left_coords = draw_tracked(left_lines, left_tracker)
    right_coords = draw_tracked(right_lines, right_tracker)

    if left_coords and right_coords:
        left_x = (left_coords[0] + left_coords[2]) // 2
        right_x = (right_coords[0] + right_coords[2]) // 2
    
        # Check if lanes crossed (X pattern) or too close/far
        if left_x >= right_x:  # Lanes crossed!
            print("WARNING: Lanes crossed, resetting trackers")
            reset_trackers()
            left_coords = None
            right_coords = None
        elif (right_x - left_x) < w * 0.2:  # Too close
            print("WARNING: Lanes too close, resetting trackers")
            reset_trackers()
            left_coords = None
            right_coords = None
        elif (right_x - left_x) > w * 0.8:  # Too far
            print("WARNING: Lanes too far, resetting trackers")
            reset_trackers()
            left_coords = None
            right_coords = None

    for coords in [left_coords, right_coords]:
        if coords:
            x1,y1,x2,y2 = coords
            cv2.line(line_img, (x1,y1),(x2,y2),(0,255,0),5)
            cv2.line(binary_lane,(x1,y1),(x2,y2),255,5)

    annotated = cv2.addWeighted(img, 0.8, line_img,1,0)
    if return_binary:
        return annotated, binary_lane, (left_coords, right_coords)
    return annotated

# ------------------------
# Lane center estimation
# ------------------------

#Global variables for lane center estimation
lane_center_history = []
MAX_LANE_CENTER_JUMP = 50


def estimate_lane_center(binary_lane_img, lane_coords=None):
    global lane_center_history
    h, w = binary_lane_img.shape
    roi = binary_lane_img[h//2:, :]
    ys, xs = np.where(roi > 0)
    
    # No lanes detected
    if len(xs) < 50:
        if len(lane_center_history) > 0:
            return int(np.mean(lane_center_history))
        return None
    
    frame_center = w // 2
    left_xs = xs[xs < frame_center]
    right_xs = xs[xs > frame_center]
    
    # Calculate new center
    if len(left_xs) > 30 and len(right_xs) > 30:
        new_lane_center = int((np.mean(left_xs) + np.mean(right_xs)) / 2)
        
        # REJECT UNREALISTIC JUMPS
        if len(lane_center_history) > 0:
            last_center = int(np.mean(lane_center_history))
            jump = abs(new_lane_center - last_center)
            if jump > MAX_LANE_CENTER_JUMP:
                print(f"WARNING: Lane center jumped {jump}px, using last valid center")
                return last_center  # Use last valid instead of bad detection
        
        lane_center = new_lane_center
    elif len(lane_center_history) > 0:
        # Fallback to history
        lane_center = int(np.mean(lane_center_history))
    else:
        return frame_center
    
    # Add to history with longer buffer
    lane_center_history.append(lane_center)
    if len(lane_center_history) > 20:  # Increased from 10
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
