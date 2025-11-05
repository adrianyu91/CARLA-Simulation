# CARLA Simulation Project

This repository contains scripts for controlling a vehicle in **CARLA 0.9.15**, collecting driving data (speed, acceleration, steering), and visualizing it in real time with **Matplotlib** and **Pygame**.  

---

## Features

- Spawn a vehicle in CARLA and control it programmatically (throttle, steering, braking).  
- View the car's perspective in a live Pygame window.  
- Log vehicle data (speed, acceleration, steering) to plots in real time.  
- Save driving data to CSV and generate final plots when the car stops.  

---

## Setup

### 1. Clone the repository

```bash
git clone git@github.com:adrianyu91/CARLA-Simulation.git
cd CARLA-Simulation
```

### 2. Set up a Python virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
# or
source .venv/bin/activate   # Linux / macOS
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install carla==0.9.15
python -m pip install matplotlib numpy pygame
```

### 4. Start CARLA
```bash
# On Windows, navigate to CARLA_0.9.15\WindowsNoEditor
# and run
CarlaUE4.exe
```

## Usage
Usage

### 1. Navigate to the task folder:
```
cd PythonAPI/Task2
```

### 2. Activate the virtual environment:
```
.venv\Scripts\activate
```

### 3. Run the simulation:
```
python driving-data.py
```
- A Pygame window will show the car’s camera view.
- A Matplotlib window will show real-time driving data (speed, acceleration, steering).
- Once the car stops, the plot will be saved and data logged to CSV.

## Notes

- Tested on CARLA 0.9.15. Using other versions may cause API mismatches.
- The Pygame and Matplotlib windows are interactive; you can close them manually to stop the simulation.
- Make sure you have at least one spawn point in the loaded map.





