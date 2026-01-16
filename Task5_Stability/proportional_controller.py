# proportional_controller.py

import numpy as np

class PDController:
    """PD Controller with temporal smoothing and rate limiting for stable lane keeping."""
    
    def __init__(self, Kp=0.0025, Kd=0.0008, smoothing_window=20, max_steering_change=0.02):
        self.Kp = Kp
        self.Kd = Kd
        self.smoothing_window = smoothing_window
        self.max_steering_change = max_steering_change
        
        self.prev_error = 0
        self.prev_steering = 0
        self.steering_history = []
        self.error_history = []
        
    def get_steering(self, lane_center_x, img_width):
        """Returns steering value between -0.5 (left) and 0.5 (right)."""
        if lane_center_x is None:
            return self.prev_steering
        
        # Calculate and smooth error
        error = lane_center_x - img_width // 2
        self.error_history.append(error)
        if len(self.error_history) > 5:
            self.error_history.pop(0)
        smoothed_error = np.mean(self.error_history)
        
        # P and D terms
        p_term = -self.Kp * smoothed_error
        d_term = -self.Kd * (smoothed_error - self.prev_error)
        self.prev_error = smoothed_error
        
        steering = p_term + d_term
        steering = max(min(steering, 0.5), -0.5)
        
        # Rate limiting
        steering_change = steering - self.prev_steering
        if abs(steering_change) > self.max_steering_change:
            steering = self.prev_steering + np.sign(steering_change) * self.max_steering_change
        self.prev_steering = steering
        
        # Temporal smoothing
        self.steering_history.append(steering)
        if len(self.steering_history) > self.smoothing_window:
            self.steering_history.pop(0)
        
        return np.mean(self.steering_history)
    
    def reset(self):
        self.prev_error = 0
        self.prev_steering = 0
        self.steering_history = []
        self.error_history = []


class ProportionalController:
    """Simple proportional controller with enhanced smoothing."""
    
    def __init__(self, Kp=0.005, smoothing_window=15):
        self.Kp = Kp
        self.smoothing_window = smoothing_window
        self.steering_history = []
        self.prev_steering = 0
        
    def get_steering(self, lane_center_x, img_width):
        if lane_center_x is None:
            return self.prev_steering
            
        error = lane_center_x - img_width // 2
        steering = -self.Kp * error
        steering = max(min(steering, 0.5), -0.5)
        
        self.steering_history.append(steering)
        if len(self.steering_history) > self.smoothing_window:
            self.steering_history.pop(0)
        
        smoothed_steering = np.mean(self.steering_history)
        self.prev_steering = smoothed_steering
        return smoothed_steering
    
    def reset(self):
        self.steering_history = []
        self.prev_steering = 0


# Tuning guide
if __name__ == "__main__":
    # Oscillating? -> Decrease Kp, increase Kd or smoothing_window
    # Too slow? -> Increase Kp, decrease smoothing_window
    # Overshooting? -> Increase Kd, decrease max_steering_change
    # Jerky? -> Increase smoothing_window, decrease max_steering_change
    
    controller = PDController(Kp=0.005, Kd=0.002, smoothing_window=10, max_steering_change=0.05)
    steering = controller.get_steering(350, 640)
    print(f"Steering: {steering:.4f}")
