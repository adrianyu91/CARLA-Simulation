import os
import numpy as np
import cv2
import carla
import pygame
import time

def attach_camera(world, vehicle, root_folder, display):
    images_folder = os.path.join(root_folder, "images")
    outputs_folder = os.path.join(root_folder, "outputs")

    # Create only the folder if it doesn't exist
    os.makedirs(images_folder, exist_ok=True)
    os.makedirs(outputs_folder, exist_ok=True)

    csv_path = os.path.join(outputs_folder, "vehicle_path.csv")

    # Reset CSV
    with open(csv_path, "w") as f:
        f.write("x,y\n")

    # Camera blueprint
    camera_bp = world.get_blueprint_library().find('sensor.camera.rgb')
    camera_bp.set_attribute('image_size_x', '800')
    camera_bp.set_attribute('image_size_y', '600')
    camera_bp.set_attribute('fov', '90')
    camera_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
    camera = world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)

    camera.last_save_time = 0
    camera.saved_count = 0
    camera.max_images = 20
    camera.save_interval = 1.0  # seconds

    def callback(image):
        array = np.frombuffer(image.raw_data, dtype=np.uint8).reshape((image.height, image.width, 4))
        array = array[:, :, :3][:, :, ::-1]

        now = time.time()

        if camera.saved_count < camera.max_images and (now - camera.last_save_time) >= camera.save_interval:

            # Save image
            image_path = os.path.join(images_folder, f"img_{camera.saved_count:03d}.png")
            cv2.imwrite(image_path, array)

            # Save matching vehicle XY pose
            transform = vehicle.get_transform()
            x = transform.location.x
            y = transform.location.y

            with open(csv_path, "a") as f:
                f.write(f"{x},{y}\n")

            camera.saved_count += 1
            camera.last_save_time = now

        # Display in pygame
        surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))
        display.blit(surface, (0, 0))
        pygame.display.flip()

    camera.listen(callback)
    return camera





def attach_lidar(world, vehicle, lidar_folder):
    bp = world.get_blueprint_library().find('sensor.lidar.ray_cast')

    # Much better LiDAR settings for road visibility
    bp.set_attribute('range', '50')
    bp.set_attribute('rotation_frequency', '20')   
    bp.set_attribute('points_per_second', '80000')  
    bp.set_attribute('channels', '64')                

    # Wider vertical field-of-view to capture ground + buildings
    bp.set_attribute('upper_fov', '15')
    bp.set_attribute('lower_fov', '-40')

    transform = carla.Transform(
        carla.Location(x=0.0, y=0.0, z=1.6),        
        carla.Rotation(pitch=-15)                   
    )

    lidar = world.spawn_actor(bp, transform, attach_to=vehicle)

    count = {"i": 0}

    def callback(point_cloud):
        pts = np.frombuffer(point_cloud.raw_data, dtype=np.float32)
        pts = pts.reshape((-1, 4))
        if count["i"] < 20:
            filename = os.path.join(lidar_folder, f"pc_{count['i']:03d}.npy")
            np.save(filename, pts)
            count["i"] += 1

    lidar.listen(callback)
    return lidar

