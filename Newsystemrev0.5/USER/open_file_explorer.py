import os
import subprocess
import sys

def open_file_explorer(path):
    # For Windows, we use subprocess to open the file explorer
    if sys.platform == "win32":
        subprocess.Popen(["explorer", path])
    else:
        print(f"Unsupported platform: {sys.platform}")

# Define the path you want to open in the file explorer
path_to_open = r"J:"  # Change this to the path you want

# Open the file explorer at the specified path
open_file_explorer(path_to_open)
