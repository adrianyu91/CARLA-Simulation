import os
import numpy as np
import cv2
import carla
import pygame
import time

def attach_camera(world, vehicle, save_folder, display):
    camera_bp = world.get_blueprint_library().find('sensor.camera.rgb')
    camera_bp.set_attribute('image_size_x', '800')
    camera_bp.set_attribute('image_size_y', '600')
    camera_bp.set_attribute('fov', '90')
    camera_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
    camera = world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)

    # Track last time a picture was saved
    camera.last_save_time = 0
    camera.saved_count = 0
    camera.max_images = 20  # how many images to save
    camera.save_interval = 1.0  # seconds between saved images

    def callback(image):
        array = np.frombuffer(image.raw_data, dtype=np.uint8).reshape((image.height, image.width, 4))
        array = array[:, :, :3][:, :, ::-1]  # BGRA -> BGR

        # Save image every 'save_interval' seconds
        current_time = time.time()
        if camera.saved_count < camera.max_images and (current_time - camera.last_save_time) >= camera.save_interval:
            cv2.imwrite(os.path.join(save_folder, f"img_{camera.saved_count:03d}.png"), array)
            camera.saved_count += 1
            camera.last_save_time = current_time

        # Display in pygame
        surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))
        display.blit(surface, (0, 0))
        pygame.display.flip()

    camera.listen(callback)
    return camera


def attach_lidar(world, vehicle, lidar_folder):
    # Get blueprint
    bp = world.get_blueprint_library().find('sensor.lidar.ray_cast')

    # Set better attributes for cleaner scans
    bp.set_attribute('range', '50')                 # Max range in meters
    bp.set_attribute('rotation_frequency', '10')    # Hz
    bp.set_attribute('points_per_second', '50000')  # Higher density
    bp.set_attribute('channels', '32')             # Vertical layers
    bp.set_attribute('upper_fov', '10')            # Top vertical angle
    bp.set_attribute('lower_fov', '-30')           # Bottom vertical angle

    # Transform: slightly above roof, looking straight forward
    transform = carla.Transform(carla.Location(x=0.0, y=0.0, z=2.5), carla.Rotation(pitch=0))

    # Spawn sensor
    lidar = world.spawn_actor(bp, transform, attach_to=vehicle)

    # Save counter
    count = {"i": 0}

    # Callback function to save point clouds
    def callback(point_cloud):
        pts = np.frombuffer(point_cloud.raw_data, dtype=np.float32)
        pts = pts.reshape((-1, 4))  # x, y, z, intensity
        if count["i"] < 20:
            filename = os.path.join(lidar_folder, f"pc_{count['i']:03d}.npy")
            np.save(filename, pts)
            count["i"] += 1

    # Listen to LiDAR
    lidar.listen(callback)
    return lidar
