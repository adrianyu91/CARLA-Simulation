import numpy as np
import matplotlib.pyplot as plt
import os

def generate_lidar_plots(lidar_folder, output_folder):
    # Make sure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Find all .npy files in lidar folder
    files = sorted([f for f in os.listdir(lidar_folder) if f.lower().endswith('.npy')])
    print("Looking in folder:", lidar_folder)
    print("Found .npy files:", files)

    if not files:
        print("No LiDAR files found! Make sure your main script saved .npy files to this folder.")
        return

    # Process each LiDAR file
    for i, file in enumerate(files):
        file_path = os.path.join(lidar_folder, file)
        points = np.load(file_path)

        if points.size == 0:
            print(f"File {file} is empty, skipping.")
            continue

        x = points[:, 0]
        y = points[:, 1]
        z = points[:, 2]

        mask = (x > 0) & (x < 50) & (y > -20) & (y < 20) & (z > -1) & (z < 3)

        x_filtered = x[mask]
        y_filtered = y[mask]

        # Create 2D bird's-eye view plot
        plt.figure(figsize=(6, 6))
        plt.scatter(x_filtered, y_filtered, s=1)
        plt.title(f"LIDAR Bird's Eye View - {file}")
        plt.xlabel("X (forward)")
        plt.ylabel("Y (left/right)")
        plt.axis("equal")
        plt.grid(True)

        # Save figure
        save_path = os.path.join(output_folder, f"lidar_frame_{i:02d}.png")
        plt.savefig(save_path, dpi=300)
        plt.close()
        print(f"Saved {save_path}")

    print("All LiDAR plots saved to:", output_folder)

if __name__ == "__main__":
    base = os.path.dirname(os.path.abspath(__file__))
    lidar_folder = os.path.join(base, "lidar")           # where your .npy files are
    output_folder = os.path.join(base, "lidar_plots")    # where to save plots
    generate_lidar_plots(lidar_folder, output_folder)
    input("Press Enter to exit...")
