import matplotlib.pyplot as plt

def plot_vehicle_path(location_data, save_path="vehicle_path.png", x_min=None, x_max=None, y_padding=5):
    xs = [loc[0] for loc in location_data]
    ys = [loc[1] for loc in location_data]

    plt.figure(figsize=(10, 6))
    plt.plot(ys, xs, linewidth=2)
    plt.xlabel("X Position")
    plt.ylabel("Y Position")
    plt.title("Vehicle Path")
    plt.grid(True)

    # Set custom X-axis limits
    if x_min is None:
        x_min = min(ys) - 10
    if x_max is None:
        x_max = max(ys) + (max(ys) - min(ys)) * 0.2  # extend 20% beyond max
    plt.xlim(x_min, x_max)

    # Compress Y-axis relative to X-axis
    ax = plt.gca()
    ax.set_aspect(0.3)  # compress Y relative to X

    # Expand Y-axis limits a bit so more range is visible
    y_min, y_max = min(xs), max(xs)
    ax.set_ylim(y_min - y_padding, y_max + y_padding)

    plt.savefig(save_path)
    plt.close()
