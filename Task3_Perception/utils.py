import os

def ensure_dir(folder):
    os.makedirs(folder, exist_ok=True)
