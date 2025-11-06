# Task 2 Simulation - CARLA Vehicle Control

This folder contains a Python simulation that spawns a vehicle in CARLA, controls it programmatically, tracks its motion, and logs data. The vehicle’s speed, steering, and acceleration are tracked in real time and plotted using Matplotlib.

---

## Overview

The simulation performs the following tasks:

1. Connects to the CARLA simulator (v0.9.15) and spawns a vehicle at a predefined spawn point.
2. Attaches a front-facing camera to the vehicle using CARLA's RGB camera sensor.
3. Controls the vehicle programmatically for a set sequence of movements:
   - Drive straight
   - Turn right
   - Continue straight
   - Stop
4. Logs motion data (speed, throttle, steering, brake, position) in real time.
5. Displays the camera feed via Pygame.
6. Plots the speed, throttle (acceleration proxy), and steering over time in Matplotlib.
7. Saves logged data to a CSV file (`driving_data.csv`) and the final plot (`driving_plot.png`) at the end of the simulation.

---

## Environment Setup

1. Create and activate a Python virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
```

2. Install required Python Packages:
```bash
python -m pip install carla==0.9.15
python -m pip install matplotlib
python -m pip install pygame
```
3. Launch CARLA server before running the simulation
```bash
./CARLAUE4.exe
```

## Running the Simulation
```bash
python driving_data.py
```
- The vehicle will execute a pre-programmed sequence for 18 seconds.
- pygame displays the vehicle camera view.
- Matplotlib shows real-time plots of speed, throttle, and steering.
- Logged data is printed to the console and saved to a CSV file.
- A final plot is saved as [Driving Plot.png](https://github.com/adrianyu91/CARLA-Simulation/blob/main/Task2/driving_plot.png)



## File Structure
```graphql
Task2_Simulation/
│
├─ driving_data.py        # Main Python simulation script
├─ driving_data.csv       # Generated CSV data file (after running)
├─ driving_plot.png       # Generated plot (after running)
└─ README.md             # This file
```

## Notes
- This simulation was developed and tested with CARLA 0.9.15.
- Ensure CARLA server is running before executing the script.
- Adjust camera positions or vehicle blueprint as needed for different vehicles.
