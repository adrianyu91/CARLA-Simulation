# proportional_controller.py
class ProportionalController:
    def __init__(self, Kp=0.005):
        """
        Kp: proportional gain (tune this value)
        """
        self.Kp = Kp

    def get_steering(self, lane_center_x, img_width):
        """
        Returns a steering value between -1 (left) and 1 (right)
        """
        error = lane_center_x - img_width // 2
        steering = -self.Kp * error  # negative because image X axis is left->right
        steering = max(min(steering, 0.5), -0.5)  # clamp to [-1,1]
        return steering