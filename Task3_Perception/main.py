import os
import time
import csv
import pygame
import numpy as np
import matplotlib.pyplot as plt
import carla

from sensors import attach_camera, attach_lidar
from utils import ensure_dir
from lane_detection import process_lane_images
from visualize_lidar import generate_lidar_plots

def main():
    # ------------------------
    # Setup folders
    # ------------------------
    base = os.getcwd()  # current folder
    image_folder = os.path.join(base, "images")
    lidar_folder = os.path.join(base, "lidar")
    ensure_dir(image_folder)
    ensure_dir(lidar_folder)

    output_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
    ensure_dir(output_folder)

    # ------------------------
    # Pygame setup
    # ------------------------
    os.environ['SDL_VIDEO_WINDOW_POS'] = "100,100"
    pygame.init()
    display = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Car Camera View")

    # ------------------------
    # Connect to CARLA
    # ------------------------
    client = carla.Client('localhost', 2000)
    client.set_timeout(5.0)
    world = client.get_world()
    bp_lib = world.get_blueprint_library()

    # Spawn vehicle
    vehicle_bp = bp_lib.filter('vehicle.*')[0]
    spawn = world.get_map().get_spawn_points()[0]
    vehicle = world.try_spawn_actor(vehicle_bp, spawn)
    if vehicle is None:
        raise Exception("Failed to spawn vehicle")

    # ------------------------
    # Attach Sensors
    # ------------------------
    camera = attach_camera(world, vehicle, base, display)
    lidar = attach_lidar(world, vehicle, lidar_folder)

    # ------------------------
    # Matplotlib setup
    # ------------------------
    plt.ion()
    fig, axes = plt.subplots(3, 1, figsize=(8, 6))
    line_speed, = axes[0].plot([], [])
    line_acc, = axes[1].plot([], [])
    line_steer, = axes[2].plot([], [])

    axes[0].set_ylabel("Speed (m/s)")
    axes[1].set_ylabel("Acceleration")
    axes[2].set_ylabel("Steering")
    axes[2].set_xlabel("Time (s)")
    plt.tight_layout()

    time_data = []
    speed_data = []
    acc_data = []
    steer_data = []
    location_data = []

    start = time.time()

    try:
        clock = pygame.time.Clock()
        running = True

        while running:
            t = time.time() - start

            # ------------------------
            # Vehicle movement script
            # ------------------------
            if t < 3:
                vehicle.apply_control(carla.VehicleControl(throttle=0.7))
            elif t < 7:
                vehicle.apply_control(carla.VehicleControl(throttle=0.4, steer=0.3))
            elif t < 14:
                vehicle.apply_control(carla.VehicleControl(throttle=0.7))
            else:
                vehicle.apply_control(carla.VehicleControl(brake=1.0))

            # ------------------------
            # Log telemetry
            # ------------------------
            vel = vehicle.get_velocity()
            speed = np.sqrt(vel.x**2 + vel.y**2 + vel.z**2)
            loc = vehicle.get_location()
            ctrl = vehicle.get_control()

            time_data.append(t)
            speed_data.append(speed)
            acc_data.append(ctrl.throttle)
            steer_data.append(ctrl.steer)
            location_data.append((loc.x, loc.y, loc.z))

            # Update plots
            line_speed.set_data(time_data, speed_data)
            line_acc.set_data(time_data, acc_data)
            line_steer.set_data(time_data, steer_data)
            for ax in axes:
                ax.relim()
                ax.autoscale_view()
            plt.pause(0.001)

            # Pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = False

            if t > 18:
                running = False

            clock.tick(30)

    finally:
        import traceback

        # ------------------------
        # Create outputs folder
        # ------------------------
        output_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
        ensure_dir(output_folder)

        # ------------------------
        # Save CSV
        # ------------------------
        try:
            csv_path = os.path.join(output_folder, "driving_data.csv")
            with open(csv_path, "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["Time", "Speed", "Throttle", "Steer", "X", "Y", "Z"])
                for i in range(len(time_data)):
                    x, y, z = location_data[i]
                    w.writerow([time_data[i], speed_data[i], acc_data[i], steer_data[i], x, y, z])
            print("Saved CSV:", csv_path)
        except Exception:
            print("Failed to save CSV:")
            traceback.print_exc()

        # ------------------------
        # Save speed/acc/steer plot
        # ------------------------
        try:
            plot_path = os.path.join(output_folder, "plots_speed.png")
            plt.savefig(plot_path)
            print("Saved speed/acc/steer plot:", plot_path)
        except Exception:
            print("Failed to save plots:")
            traceback.print_exc()

        # ------------------------
        # Run Lane Detection
        # ------------------------
        try:
            annotated_folder = os.path.join(base, "annotated_images")
            ensure_dir(annotated_folder)
            process_lane_images(image_folder, annotated_folder)
            print("Lane detection completed. Annotated images in:", annotated_folder)
        except Exception:
            print("Lane detection failed:")
            traceback.print_exc()

        # ------------------------
        # Plot vehicle path
        # ------------------------
        try:
            path_plot_path = os.path.join(output_folder, "vehicle_path.png")
            print("Vehicle path plot saved:", path_plot_path)
        except Exception:
            print("Vehicle path plot failed:")
            traceback.print_exc()

        # ------------------------
        # Cleanup CARLA + Pygame
        # ------------------------
        for sensor, name in [(camera, "Camera"), (lidar, "LiDAR")]:
            try:
                sensor.stop()
                sensor.destroy()
                print(f"{name} destroyed.")
            except Exception:
                print(f"Failed to destroy {name}:")
                traceback.print_exc()

        try:
            vehicle.destroy()
            print("Vehicle destroyed.")
        except Exception:
            print("Failed to destroy vehicle:")
            traceback.print_exc()

        try:
            pygame.quit()
            print("Pygame quit.")
        except Exception:
            print("Failed to quit Pygame:")
            traceback.print_exc()

        print("Cleanup complete.")


if __name__ == "__main__":
    main()
