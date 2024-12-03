import tkinter as tk
from tkinter import ttk, font, messagebox
import json
import os
import subprocess

# Define the configuration file path
CONFIG_FILE = "visual_settings.json"

# Default visual settings
default_settings = {
    "font_family": "Arial",
    "font_size": 12,
    "bg_color": "#ffffff",
    "fg_color": "#000000",
    "button_bg_color": "#f0f0f0",
    "button_fg_color": "#000000"
}

# Load settings from the configuration file
def load_settings():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as file:
                loaded_settings = json.load(file)
            # Merge loaded settings with defaults to fill missing keys
            for key, value in default_settings.items():
                loaded_settings.setdefault(key, value)
            return loaded_settings
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load settings: {e}")
    return default_settings

# Save settings to the configuration file
def save_settings(settings):
    try:
        with open(CONFIG_FILE, "w") as file:
            json.dump(settings, file, indent=4)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save settings: {e}")

# Function to close all windows and open mainui.py
def open_mainui():
    try:
        subprocess.Popen(["python", "mainui.py"])
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open mainui.py: {e}")
    finally:
        root.destroy()

# Main settings editor GUI
def settings_editor():
    current_settings = load_settings()

    def apply_changes():
        # Save the settings based on user input
        current_settings["font_family"] = font_family_var.get()
        current_settings["font_size"] = int(font_size_var.get())
        current_settings["bg_color"] = bg_color_var.get()
        current_settings["fg_color"] = fg_color_var.get()
        current_settings["button_bg_color"] = button_bg_color_var.get()
        current_settings["button_fg_color"] = button_fg_color_var.get()

        save_settings(current_settings)
        messagebox.showinfo("Settings", "Settings saved successfully!")
        open_mainui()  # Close and open mainui

    # Initialize the settings editor window
    global root
    root = tk.Tk()
    root.title("Visual Settings Editor")
    root.geometry("400x450")  # Increased height to fit the Apply button

    tk.Label(root, text="Visual Settings Editor", font=("Arial", 16, "bold")).pack(pady=10)

    # Font Family
    tk.Label(root, text="Font Family").pack(anchor="w", padx=10)
    font_family_var = tk.StringVar(value=current_settings["font_family"])
    font_family_combobox = ttk.Combobox(root, textvariable=font_family_var, values=font.families())
    font_family_combobox.pack(fill="x", padx=10, pady=5)

    # Font Size
    tk.Label(root, text="Font Size").pack(anchor="w", padx=10)
    font_size_var = tk.StringVar(value=current_settings["font_size"])
    font_size_spinbox = ttk.Spinbox(root, from_=8, to=50, textvariable=font_size_var)
    font_size_spinbox.pack(fill="x", padx=10, pady=5)

    # Background Color
    tk.Label(root, text="Background Color (Hex)").pack(anchor="w", padx=10)
    bg_color_var = tk.StringVar(value=current_settings["bg_color"])
    bg_color_entry = tk.Entry(root, textvariable=bg_color_var)
    bg_color_entry.pack(fill="x", padx=10, pady=5)

    # Foreground Color
    tk.Label(root, text="Foreground Color (Hex)").pack(anchor="w", padx=10)
    fg_color_var = tk.StringVar(value=current_settings["fg_color"])
    fg_color_entry = tk.Entry(root, textvariable=fg_color_var)
    fg_color_entry.pack(fill="x", padx=10, pady=5)

    # Button Background Color
    tk.Label(root, text="Button Background Color (Hex)").pack(anchor="w", padx=10)
    button_bg_color_var = tk.StringVar(value=current_settings["button_bg_color"])
    button_bg_color_entry = tk.Entry(root, textvariable=button_bg_color_var)
    button_bg_color_entry.pack(fill="x", padx=10, pady=5)

    # Button Foreground Color
    tk.Label(root, text="Button Foreground Color (Hex)").pack(anchor="w", padx=10)
    button_fg_color_var = tk.StringVar(value=current_settings["button_fg_color"])
    button_fg_color_entry = tk.Entry(root, textvariable=button_fg_color_var)
    button_fg_color_entry.pack(fill="x", padx=10, pady=5)

    # Apply Button
    tk.Button(root, text="Apply and Save", command=apply_changes).pack(pady=20)

    # Override the close button (X) to open mainui
    root.protocol("WM_DELETE_WINDOW", open_mainui)

    root.mainloop()

if __name__ == "__main__":
    settings_editor()
