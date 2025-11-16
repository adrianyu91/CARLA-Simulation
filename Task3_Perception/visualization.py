import matplotlib.pyplot as plt

def plot_vehicle_path(location_data, save_path="vehicle_path.png", x_min=None, x_max=None):
    xs = [loc[0] for loc in location_data]
    ys = [loc[1] for loc in location_data]

    plt.figure(figsize=(8, 6))
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
    plt.gca().set_aspect('auto')  # allow stretching

    plt.savefig(save_path)
    plt.close()
