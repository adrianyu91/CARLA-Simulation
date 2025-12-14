import carla

def main():
    client = carla.Client("localhost", 2000)
    client.set_timeout(5.0)

    world = client.get_world()
    actors = world.get_actors()

    sensors = actors.filter("sensor.*")
    vehicles = actors.filter("vehicle.*")

    print("\n--- CLEANUP STARTED ---")

    # Destroy all sensors
    if len(sensors) > 0:
        print(f"Destroying {len(sensors)} sensors...")
        for s in sensors:
            try:
                s.destroy()
            except:
                pass
    else:
        print("No sensors to destroy.")

    # Destroy all vehicles EXCEPT NPCs if you want
    # If you want to destroy ONLY YOUR vehicle, keep the filter commented
    if len(vehicles) > 0:
        print(f"Destroying {len(vehicles)} vehicles...")
        for v in vehicles:
            try:
                v.destroy()
            except:
                pass
    else:
        print("No vehicles to destroy.")

    print("--- CLEANUP COMPLETE ---\n")

if __name__ == "__main__":
    main()
