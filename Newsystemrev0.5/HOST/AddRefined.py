import tkinter as tk
from tkinter import messagebox, ttk
import requests
import json
import re

# Server configuration
FLASK_SERVER_URL = "http://<flask-server-ip>:5000"  # Replace <flask-server-ip> with your server's IP address

# Sanitize property names
def sanitize_name(name):
    """Replace all non-alphanumeric characters with underscores."""
    return re.sub(r"[^a-zA-Z0-9]", "_", name)

# Fetch available properties from the Flask server
def get_available_properties():
    """Retrieve headers and property values from the Flask server."""
    try:
        response = requests.get(f"{FLASK_SERVER_URL}/list_headers")
        if response.status_code == 200:
            headers = response.json().get("headers", [])
            property_files = {sanitize_name(header): header for header in headers}
            return property_files
        else:
            messagebox.showerror("Error", f"Failed to fetch headers: {response.text}")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Error connecting to server: {e}")
    return {}

# Fetch property values from the Flask server
def get_property_values(property_name):
    """Retrieve values for a specific property from the server."""
    try:
        response = requests.get(f"{FLASK_SERVER_URL}/list_refined")
        if response.status_code == 200:
            refined_files = response.json().get("files", {})
            sanitized_name = sanitize_name(property_name)
            return refined_files.get(f"{sanitized_name}.txt", [])
        else:
            messagebox.showerror("Error", f"Failed to fetch property values: {response.text}")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Error connecting to server: {e}")
    return []

# Load visual settings from configuration file
def load_visual_settings():
    """Load UI visual settings from a JSON file."""
    config_file = "visual_settings.json"
    default_settings = {
        "font_family": "Arial",
        "font_size": 12,
        "bg_color": "#ffffff",
        "fg_color": "#000000",
        "button_bg_color": "#f0f0f0",
        "button_fg_color": "#000000"
    }
    try:
        if os.path.exists(config_file):
            with open(config_file, "r") as file:
                settings = json.load(file)
                for key, value in default_settings.items():
                    settings.setdefault(key, value)  # Ensure all keys are present
                return settings
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load visual settings: {e}")
    return default_settings

# Apply visual settings to a widget
def apply_visual_settings(widget, settings, is_button=False):
    """Apply visual settings to a widget."""
    widget.configure(
        font=(settings["font_family"], settings["font_size"]),
        bg=settings["button_bg_color"] if is_button else settings["bg_color"],
        fg=settings["button_fg_color"] if is_button else settings["fg_color"]
    )

# Function to add a new value to the selected property on the server
def add_value(settings):
    """Add a new value to the selected property via the server."""
    selected_property = property_var.get()
    new_value = entry_value.get().strip()

    if not selected_property or not new_value:
        messagebox.showerror("Error", "Please select a property and enter a value.")
        return

    sanitized_property = sanitize_name(selected_property)
    try:
        # Send the new value to the server
        response = requests.post(
            f"{FLASK_SERVER_URL}/submit_data",
            json={sanitized_property: new_value}
        )
        if response.status_code == 200:
            messagebox.showinfo("Success", f"'{new_value}' added to {selected_property}.")
            entry_value.delete(0, tk.END)  # Clear the entry field
        else:
            messagebox.showerror("Error", f"Failed to add value: {response.text}")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Error connecting to server: {e}")

# Tkinter UI setup
def setup_ui():
    """Set up the Tkinter UI."""
    global property_var, entry_value

    # Load visual settings
    settings = load_visual_settings()

    root = tk.Tk()
    root.title("Add New Value to Refined Properties")
    root.configure(bg=settings["bg_color"])

    # Fetch properties from the server
    properties = get_available_properties()
    if not properties:
        messagebox.showerror("Error", "Failed to fetch properties. Exiting.")
        root.destroy()
        return

    # Apply visual settings to labels and dropdowns
    tk.Label(root, text="Select Property:", bg=settings["bg_color"], fg=settings["fg_color"], 
             font=(settings["font_family"], settings["font_size"])).grid(row=0, column=0, padx=10, pady=5)
    
    property_var = tk.StringVar()
    property_dropdown = ttk.Combobox(root, textvariable=property_var, values=list(properties.values()))
    property_dropdown.grid(row=0, column=1, padx=10, pady=5)
    if properties:
        property_dropdown.set(list(properties.values())[0])  # Set default selection

    tk.Label(root, text="New Value:", bg=settings["bg_color"], fg=settings["fg_color"], 
             font=(settings["font_family"], settings["font_size"])).grid(row=1, column=0, padx=10, pady=5)
    
    entry_value = tk.Entry(root, width=30)
    entry_value.grid(row=1, column=1, padx=10, pady=5)

    add_button = tk.Button(root, text="Add Value", command=lambda: add_value(settings))
    apply_visual_settings(add_button, settings, is_button=True)  # Apply button-specific visual settings
    add_button.grid(row=2, column=0, columnspan=2, pady=10)

    root.mainloop()

# Run the UI
setup_ui()
