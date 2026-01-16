import os
import time
import csv
import numpy as np
import cv2
import pygame
import carla

from sensors import attach_camera, attach_lidar
from utils import ensure_dir
from proportional_controller import PDController
from lane_detection import detect_lanes, estimate_lane_center

lane_center_history = []

def main():
    base = os.getcwd()
    image_folder = os.path.join(base, "images")
    lidar_folder = os.path.join(base, "lidar")
    ensure_dir(image_folder)
    ensure_dir(lidar_folder)
    output_folder = os.path.join(base, "outputs")
    ensure_dir(output_folder)

    pygame.init()
    display = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Car Camera View")

    # Connect to CARLA
    client = carla.Client('localhost', 2000)
    client.set_timeout(5.0)
    world = client.get_world()
    bp_lib = world.get_blueprint_library()

    # Spawn vehicle
    vehicle_bp = bp_lib.filter('vehicle.*')[0]
    spawn = world.get_map().get_spawn_points()[0]
    spawn.location.x += 30
    spawn.location.y += 0
    spawn.location.z = 1.0
    vehicle = world.try_spawn_actor(vehicle_bp, spawn)
    if vehicle is None:
        raise Exception("Failed to spawn vehicle")

    # Attach sensors
    camera = attach_camera(world, vehicle, base)
    lidar = attach_lidar(world, vehicle, lidar_folder)

    # Controller
    controller = PDController(Kp=0.005, Kd=0.002, smoothing_window=10, max_steering_change=0.05)

    clock = pygame.time.Clock()
    running = True

    try:
        while running:
            if hasattr(camera, "last_frame") and camera.last_frame is not None:
                frame = camera.last_frame.copy()
                annotated, binary_lane, lane_coords = detect_lanes(frame, return_binary=True)
                lane_center = estimate_lane_center(binary_lane, lane_coords)
                
                if lane_center is None:
                    lane_center = frame.shape[1] // 2

                error = lane_center - frame.shape[1] // 2
                steer = controller.get_steering(lane_center, frame.shape[1])

                # Debug prints
                print(f"Lane center: {lane_center}, Error: {error}, Steer: {steer:.3f}, Non-zero lane pixels: {np.count_nonzero(binary_lane)}")

            else:
                annotated = np.zeros((600, 800, 3), dtype=np.uint8)
                steer = 0.0

            # Apply control
            control = carla.VehicleControl()
            control.throttle = 0.5
            control.steer = steer
            vehicle.apply_control(control)

            # Display annotated image
            frame_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
            surface = pygame.surfarray.make_surface(np.rot90(frame_rgb))
            display.blit(surface, (0, 0))
            pygame.display.flip()

            # Pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = False

            clock.tick(30)

    finally:
        # Cleanup
        for sensor in [camera, lidar]:
            try:
                sensor.stop()
                sensor.destroy()
            except:
                pass
        try:
            vehicle.destroy()
        except:
            pass
        pygame.quit()

if __name__ == "__main__":
    main()