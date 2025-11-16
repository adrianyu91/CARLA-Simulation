# Task 3 – Basic Perception and Lane Following Prep

This task demonstrates basic vehicle perception in CARLA using cameras and LiDAR, along with lane detection and vehicle path visualization.

---

## Directory Structure
```graphql
Task3_Perception/
├── images/              # Raw RGB camera frames captured during the simulation
├── lidar/               # LiDAR point cloud data (.npy files)
├── outputs/             # CSV logs, plots, and processed results
├── annotated_images/    # Images with lane detection overlay
├── lidar_plots/         # 3D visualizations of LiDAR scans
├── main.py              # Main script to run the simulation and logging
├── sensors.py           # Functions to attach camera and LiDAR sensors
├── lane_detection.py    # Processes camera frames to detect lane lines
├── visualization.py     # Plots vehicle path and other visualizations
├── visualize_lidar.py   # Script to generate LiDAR 3D plots
└── utils.py             # Utility functions (e.g., folder creation)
```
## How to Run

1. Setup CARLA
Make sure CARLA 0.9.15 is running and PythonAPI is accessible.

2. Run the main simulation
```bash

python main.py

```
- Captures 20 RGB camera images in images/
- Captures 20 LiDAR point cloud frames in lidar/
- Logs speed, throttle, steering, and vehicle positions to outputs/driving_data.csv
- Generates plots of vehicle path and telemetry in outputs/
- Produces lane-detected images in annotated_images/

3. Visualize LiDAR scans (optional)
```bash

python visualize_lidar.py

```
Saves 3D point cloud plots to lidar_plots/

## Outputs

**CSV Logs**: outputs/driving_data.csv – vehicle speed, throttle, steering, and locations.
**Graphs**: Vehicle path plot and telemetry plots (outputs/).
**Lane Detection:** Annotated images in annotated_images/.
**LiDAR**: Raw .npy frames in lidar/, visualized in lidar_plots/.
