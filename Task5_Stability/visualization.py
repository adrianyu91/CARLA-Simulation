import os
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.image import imread

# -----------------------------
# Paths
# -----------------------------
base_folder = os.getcwd()  # Adjust if needed
csv_path = os.path.join(base_folder, "outputs", "vehicle_path.csv")
bev_image_path = os.path.join(base_folder, "outputs", "birds_eye_view.png")
output_plot_path = os.path.join(base_folder, "outputs", "vehicle_path_on_bev.png")

# -----------------------------
# Load vehicle path from CSV
# -----------------------------
x_list, y_list = [], []

with open(csv_path, "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        x_list.append(float(row["x"]))
        y_list.append(float(row["y"]))

x_list = np.array(x_list)
y_list = np.array(y_list)

# Swap X and Y for correct orientation
x_plot = y_list
y_plot = x_list

# -----------------------------
# Load bird's-eye view image
# -----------------------------
bev_img = imread(bev_image_path)

# -----------------------------
# Plot vehicle path on top
# -----------------------------
plt.figure(figsize=(10, 10))
y_offset = -2.0  # negative to shift down, tweak as needed

plt.imshow(
    bev_img, 
    extent=[x_plot.min()-5, x_plot.max()+5, y_plot.min()-5 + y_offset, y_plot.max()+5 +y_offset]
)
plt.plot(x_plot, y_plot, marker='o', markersize=4, color='red', label='Vehicle Path')

plt.xlabel("X (forward)")
plt.ylabel("Y (left/right)")
plt.title("Vehicle Path on Bird's Eye View")
plt.axis("equal")
plt.grid(True)
plt.legend()

plt.savefig(output_plot_path, dpi=300)
plt.show()

print("Vehicle path plot saved to:", output_plot_path)
