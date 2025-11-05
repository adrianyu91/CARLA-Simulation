import os
import carla
import pygame
import numpy as np
import matplotlib.pyplot as plt
import time
import csv


def main():
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
    blueprint_library = world.get_blueprint_library()

    # Spawn vehicle
    vehicle_bp = blueprint_library.filter('vehicle.*')[0]
    spawn_point = world.get_map().get_spawn_points()[0]
    vehicle = world.try_spawn_actor(vehicle_bp, spawn_point)
    if vehicle is None:
        raise Exception("Failed to spawn vehicle")

    # Camera
    camera_bp = blueprint_library.find('sensor.camera.rgb')
    camera_bp.set_attribute('image_size_x', '800')
    camera_bp.set_attribute('image_size_y', '600')
    camera_bp.set_attribute('fov', '90')
    camera_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
    camera = world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)

    # ------------------------
    # Matplotlib setup
    # ------------------------
    plt.ion()  # interactive mode
    fig, axes = plt.subplots(3, 1, figsize=(8, 6))
    line_speed, = axes[0].plot([], [], label='Speed')
    axes[0].set_ylabel('Speed (m/s)')
    axes[0].set_title('Speed over Time')
    line_acc, = axes[1].plot([], [], label='Acceleration')
    axes[1].set_ylabel('Acceleration (m/s²)')
    axes[1].set_title('Acceleration over Time')
    line_steer, = axes[2].plot([], [], label='Steering')
    axes[2].set_ylabel('Steering (rad)')
    axes[2].set_xlabel('Time (s)')
    axes[2].set_title('Steering over Time')
    plt.tight_layout()

    try:
        mngr = plt.get_current_fig_manager()
        mngr.window.wm_geometry("+1400+100")  # Adjust position: x=850, y=100
    except Exception as e:
        print(f"Could not reposition Matplotlib window: {e}")

    time_data = []
    speed_data = []
    acc_data = []
    steer_data = []
    location_data = []

    start_time = time.time()

    # ------------------------
    # Camera callback
    # ------------------------
    def display_image(image):
        array = np.frombuffer(image.raw_data, dtype=np.uint8)
        array = array.reshape((image.height, image.width, 4))
        array = array[:, :, :3]       # drop alpha
        array = array[:, :, ::-1]     # BGR -> RGB
        surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))
        display.blit(surface, (0, 0))
        pygame.display.flip()

    camera.listen(display_image)

    # ------------------------
    # Simulation loop
    # ------------------------
    try:
        clock = pygame.time.Clock()
        running = True
        while running:
            t = time.time() - start_time

            # Update vehicle control
            if t < 3: #drive straight for 5 seconds
                vehicle.apply_control(carla.VehicleControl(throttle=0.7, steer=0.0))
            elif t < 7: #turn right for next 3 seconds
                vehicle.apply_control(carla.VehicleControl(throttle=0.4, steer=0.3))
            elif t < 14: #Drive straight for next 4 seconds
                vehicle.apply_control(carla.VehicleControl(throttle=0.7, steer=0.0))
            else: #stop
                vehicle.apply_control(carla.VehicleControl(throttle=0.0, steer=0.0, brake=1.0))

            # Log data
            velocity = vehicle.get_velocity()
            speed = np.sqrt(velocity.x**2 + velocity.y**2 + velocity.z**2)
            steer = vehicle.get_control().steer
            throttle = vehicle.get_control().throttle
            brake = vehicle.get_control().brake

            location = vehicle.get_location()
            rotation = vehicle.get_transform().rotation

            time_data.append(t)
            speed_data.append(speed)
            acc_data.append(throttle)  # simple proxy
            steer_data.append(steer)
            location_data.append((location.x, location.y, location.z))

            # Print to console
            print(f"t={t:.2f}s | "
            f"Loc: x={location.x:.2f}, y={location.y:.2f}, z={location.z:.2f} | "
            f"Speed: {speed:.2f} m/s | "
            f"Throttle: {throttle:.2f} | "
            f"Steer: {steer:.2f} | "
            f"Brake: {brake:.2f} | "
            f"Yaw: {rotation.yaw:.2f}")

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

            clock.tick(30)
            # Stop running after vehicle stops
            if t > 18:
                running = False

    finally:
         # ------------------------
        # Save data to CSV
        # ------------------------
        csv_path = os.path.join(os.getcwd(), "driving_data.csv")
        with open(csv_path, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Time", "Speed", "Throttle", "Steer", "X", "Y", "Z"])
            for i in range(len(time_data)):
                writer.writerow([
                    time_data[i], speed_data[i], acc_data[i], steer_data[i],
                    location_data[i][0], location_data[i][1], location_data[i][2]
                ])
        print(f"CSV saved to {csv_path}")

        # Save final plot
        plot_path = os.path.join(os.getcwd(), "driving_plot.png")
        plt.savefig(plot_path)
        print(f"Plot saved to {plot_path}")



        camera.stop()
        camera.destroy()
        vehicle.destroy()
        pygame.quit()
        print("Cleaned up. Exiting.")

if __name__ == "__main__":
    main()
