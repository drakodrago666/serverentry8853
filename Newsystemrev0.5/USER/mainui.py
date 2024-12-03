import tkinter as tk
import subprocess
from tkinter import messagebox
import os
import json

# Determine the directory containing this script and use it as the base for relative paths
base_directory = os.path.dirname(os.path.abspath(__file__))

# Configuration file for visual settings
CONFIG_FILE = os.path.join(base_directory, "visual_settings.json")

# Default visual settings
default_settings = {
    "font_family": "Arial",
    "font_size": 12,
    "bg_color": "#ffffff",
    "fg_color": "#000000",
    "button_bg_color": "#f0f0f0",
    "button_fg_color": "#000000"
}

# Load visual settings
def load_settings():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as file:
                loaded_settings = json.load(file)
            for key, value in default_settings.items():
                loaded_settings.setdefault(key, value)
            return loaded_settings
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load settings: {e}")
    return default_settings

settings = load_settings()

# Define functions for specific scripts
def run_script(script_name):
    """Run a specific script without showing the command prompt."""
    subprocess.Popen(
        ["python", os.path.join(base_directory, script_name)],
        creationflags=subprocess.CREATE_NO_WINDOW
    )

def run_visual_settings():
    """Run the Visual Settings script and close the main UI."""
    root.destroy()  # Close the current main UI window
    subprocess.Popen(["python", os.path.join(base_directory, "Visual_Settings.py")])

# Initialize Tkinter Window
root = tk.Tk()
root.title("User Main Menu")
root.geometry("520x300")  # Adjusted window size for more buttons
root.configure(bg=settings["bg_color"])

# Explicitly define button labels and their associated scripts
# Explicitly define button labels and their associated scripts
buttons = [
    ("Add Data", lambda: run_script("USERADD.py")),
    ("Edit Data", lambda: run_script("USEREDIT.py")),
    ("Show Data", lambda: run_script("ShowData.py")),
    ("File Explorer (J:)", lambda: run_script("open_file_explorer.py")),
    ("Visual Settings", run_visual_settings),  # Add Visual Settings button that closes main UI
    ("P.O.# Finder", lambda: run_script("testpobatching.py")),  # Add P.O.# Finder button
    ("Coming Soon", None)
]


# Standard button size
button_width = 20
button_height = 2

# Create and place buttons in the window
for index, (label, command) in enumerate(buttons):
    row = index // 3
    col = index % 3
    if command:
        button = tk.Button(
            root,
            text=label,
            command=command,
            width=button_width,
            height=button_height,
            font=(settings["font_family"], settings["font_size"]),
            bg=settings["button_bg_color"],
            fg=settings["button_fg_color"]
        )
    else:
        button = tk.Button(
            root,
            text=label,
            state="disabled",
            width=button_width,
            height=button_height,
            font=(settings["font_family"], settings["font_size"]),
            bg=settings["button_bg_color"],
            fg=settings["button_fg_color"]
        )
    button.grid(row=row, column=col, padx=10, pady=5)

# Configure grid rows and columns to distribute the available space
for i in range((len(buttons) // 3) + 1):  # Adjust rows dynamically
    root.grid_rowconfigure(i, weight=1)
for i in range(3):  # Three columns
    root.grid_columnconfigure(i, weight=1)

root.mainloop()
