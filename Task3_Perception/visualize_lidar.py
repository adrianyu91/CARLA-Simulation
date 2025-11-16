import numpy as np
import matplotlib.pyplot as plt
import os

# ----------------------------
# Paths
# ----------------------------
base = os.path.dirname(os.path.abspath(__file__))
lidar_folder = os.path.join(base, "lidar")            # where your .npy files are
output_folder = os.path.join(base, "lidar_plots")    # where to save images
os.makedirs(output_folder, exist_ok=True)

# ----------------------------
# Get all LiDAR files
# ----------------------------
files = sorted([f for f in os.listdir(lidar_folder) if f.endswith('.npy')])

# ----------------------------
# Loop and save plots
# ----------------------------
for i, file in enumerate(files):
    file_path = os.path.join(lidar_folder, file)
    points = np.load(file_path)
    
    x, y, z = points[:,0], points[:,1], points[:,2]
    
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(x, y, z, s=0.5, c=z, cmap='viridis')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title(file)
    
    # Save the plot
    save_path = os.path.join(output_folder, f"lidar_frame_{i:02d}.png")
    plt.savefig(save_path)
    plt.close(fig)  # Close figure to save memory

print("All LiDAR frames saved to:", output_folder)
