import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os

# Flask server endpoint
FLASK_SERVER = "http://localhost:5000"

# File to store combobox and checkbox states
STATE_FILE = "combobox_states.json"

admin_mode = False  # Tracks if Admin mode is enabled
checkboxes = {}  # Stores checkboxes globally to be accessible in toggle_admin

def ensure_file_refined():
    # Step 1: Send the request to the Flask server
    url = 'http://localhost:5000/list_refined'  # Replace with your Flask server URL
    response = requests.get(url)

    # Check if the response is valid
    if response.status_code == 200:
        data = response.json()
        
        # Step 2: Parse the JSON data
        files_data = data.get("files", {})
        
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.realpath(__file__))
        
        # Path to the DB/Refined directory in the same folder as the script
        base_directory = os.path.join(script_dir, "DB", "Refined")
        
        # Step 3: Check if the files exist and create them if they don't
        for file_name, file_data in files_data.items():
            file_path = os.path.join(base_directory, file_name)
            
            # If the file doesn't exist, create it and write the data inside
            if not os.path.exists(file_path):
                # Create the directory if it doesn't exist
                os.makedirs(base_directory, exist_ok=True)
                
                # Write each item in file_data on a new line
                with open(file_path, 'w') as file:
                    for item in file_data:
                        file.write(f"{item}\n")  # Write each item on a new line
                print(f"Created file: {file_name} with data: {file_data}")
            else:
                print(f"File {file_name} already exists, skipping.")
    else:
        print("Failed to retrieve data from Flask server.")

# Call the function to ensure the files are created
ensure_file_refined()

# Fetch data from the Flask server
def fetch_data():
    try:
        response = requests.get(f"{FLASK_SERVER}/get_data")
        if response.status_code == 200:
            return response.json()
        else:
            messagebox.showerror("Error", f"Failed to fetch data: {response.json().get('message')}")
            return []
    except Exception as e:
        messagebox.showerror("Error", f"Could not connect to server: {e}")
        return []


# Update data on the Flask server
def update_data(so_value, updated_data):
    try:
        response = requests.post(f"{FLASK_SERVER}/update_data/{so_value}", json=updated_data)
        if response.status_code == 200:
            messagebox.showinfo("Success", response.json().get("message"))
        else:
            messagebox.showerror("Error", f"Failed to update data: {response.json().get('message')}")
    except Exception as e:
        messagebox.showerror("Error", f"Could not connect to server: {e}")


# Load combobox and checkbox states from file
def load_states():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as file:
            return json.load(file)
    return {}


# Save combobox and checkbox states to file
def save_states(new_states):
    existing_states = load_states()
    merged_states = {**existing_states, **new_states}  # Merge new states with existing ones
    with open(STATE_FILE, "w") as file:
        json.dump(merged_states, file, indent=4)


# Toggle Admin Mode
def toggle_admin():
    global admin_mode, checkboxes  # Ensure the global variables are accessed

    def check_password():
        global admin_mode  # Explicitly declare admin_mode as global in this function
        password = password_entry.get()
        if password == "8853":
            admin_mode = not admin_mode  # Toggle the admin mode
            admin_button.config(text="Disable Admin" if admin_mode else "Enable Admin")
            for checkbox in checkboxes.values():
                checkbox["state"] = "normal" if admin_mode else "disabled"
            toggle_window.destroy()
        else:
            messagebox.showerror("Error", "Incorrect password.")

    # Password entry window
    toggle_window = tk.Toplevel()
    toggle_window.title("Admin Password")
    toggle_window.geometry("300x150")
    toggle_window.resizable(False, False)
    tk.Label(toggle_window, text="Enter Admin Password:", font=("Arial", 12)).pack(pady=10)
    password_entry = ttk.Entry(toggle_window, show="*", font=("Arial", 12))
    password_entry.pack(pady=5)
    tk.Button(toggle_window, text="Submit", command=check_password, font=("Arial", 12)).pack(pady=10)


# First Window: Select S.O.# and Load
def open_main_window():
    data = fetch_data()
    if not data:
        return

    def load_entry():
        selected_so = so_combobox.get()
        if not selected_so:
            messagebox.showerror("Error", "Please select an S.O.#.")
            return
        matching_row = next((row for row in data if str(row["S.O.#"]) == selected_so), None)
        if matching_row:
            root.destroy()
            open_edit_window(matching_row)
        else:
            messagebox.showerror("Error", f"No matching data found for S.O.#: {selected_so}")

    root = tk.Tk()
    root.title("S.O.# Selection")
    root.geometry("400x200")
    root.resizable(False, False)

    tk.Label(root, text="Select S.O.#:", font=("Arial", 14, "bold")).pack(pady=20)
    so_combobox = ttk.Combobox(root, values=[str(row["S.O.#"]) for row in data], font=("Arial", 12), width=30)
    so_combobox.pack(pady=10)

    tk.Button(root, text="LOAD", command=load_entry, font=("Arial", 14), bg="#4CAF50", fg="white", width=15).pack(pady=20)
    root.mainloop()


# Directory to store the files
DB_REFINED_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "DB", "Refined")

# Ensure that the folder exists
os.makedirs(DB_REFINED_DIR, exist_ok=True)

def open_edit_window(row_data):
    global checkboxes  # Ensure the global checkboxes is accessible
    states = load_states()

    def save_changes():
        updated_data = {}
        current_states = {}
        for header, widgets in entry_widgets.items():
            combo, checkbox_var = widgets
            current_states[header] = {
                "locked": combo["state"] == "disabled",
                "checked": checkbox_var.get()
            }
            if header == "NOTES" or header == "Description" or (combo.get() != ""):  # Update NOTES and Description even when empty; update others only if a new value is selected
                if not checkbox_var.get():  # If not locked
                    updated_data[header] = combo.get() if header != "NOTES" and header != "Description" else description_text.get("1.0", "end-1c").strip()
        save_states(current_states)  # Save the current states of checkboxes and locks
        update_data(row_data["S.O.#"], updated_data)

    def toggle_lock(header):
        combo, checkbox_var = entry_widgets[header]
        combo["state"] = "disabled" if checkbox_var.get() else "normal"

        # Save state immediately when the checkbox is toggled
        new_states = {
            header: {
                "locked": combo["state"] == "disabled",
                "checked": checkbox_var.get(),
            }
        }
        save_states(new_states)

    edit_window = tk.Tk()
    edit_window.title("Edit Data")
    edit_window.geometry("900x600")
    edit_window.resizable(True, True)

    tk.Label(edit_window, text=f"Editing S.O.#: {row_data['S.O.#']}", font=("Arial", 16, "bold")).pack(pady=10)

    # Frames for layout
    left_frame = tk.Frame(edit_window, bg="#f9f9f9")
    left_frame.pack(side="left", padx=20, pady=10, fill="both", expand=True)

    right_frame = tk.Frame(edit_window, bg="#f9f9f9")
    right_frame.pack(side="right", padx=20, pady=10, fill="both", expand=True)

    # Button frame at the bottom-right of NOTES
    notes_button_frame = tk.Frame(edit_window, bg="#f9f9f9")
    notes_button_frame.pack(side="bottom", anchor="se", padx=10, pady=10)

    entry_widgets = {}
    row_idx = 0  # Row index for Notes and Description placement
    for idx, (header, value) in enumerate(row_data.items()):
        if header == "S.O.#":  # Skip editing the primary key
            continue

        # Sanitize the header for use as a file name
        sanitized_header = header.replace(" ", "_").replace("/", "_").replace("\\", "_").replace(":", "_").replace(".", "_")
        file_path = os.path.join(DB_REFINED_DIR, f"{sanitized_header}.txt")

        # Ensure the .txt file exists and create it if necessary
        if not os.path.exists(file_path):
            with open(file_path, 'w') as file:
                # Write some default content (can be adjusted based on your needs)
                file.write("")  # Empty content to initialize the file
            print(f"Created file: {file_path}")

        # Read values from the .txt file to populate the combobox
        with open(file_path, 'r') as file:
            combobox_values = [line.strip() for line in file.readlines() if line.strip()]

        if header == "NOTES" or header == "Description":  # Special handling for NOTES and Description
            tk.Label(right_frame, text=header, font=("Arial", 12, "bold"), bg="#f9f9f9").grid(row=row_idx, column=0, sticky="w", pady=5)
            description_text = tk.Text(right_frame, height=15, width=40, font=("Arial", 12))
            description_text.insert("1.0", value)
            description_text.grid(row=row_idx + 1, column=0, pady=10)
            entry_widgets[header] = (description_text, tk.BooleanVar(value=False))  # NOTES and Description don't use checkboxes
            row_idx += 2  # Skip the next row for the next field
            continue

        # Current value, Combobox, and Checkbox for other fields
        tk.Label(left_frame, text=value, font=("Arial", 12), fg="red", bg="#f9f9f9").grid(row=idx, column=0, sticky="w", pady=5, padx=10)  # Current value in red
        tk.Label(left_frame, text=f"{header}:", font=("Arial", 12, "bold"), bg="#f9f9f9").grid(row=idx, column=1, sticky="w", pady=5, padx=20)  # Header name with spacing
        combo = ttk.Combobox(left_frame, values=combobox_values, font=("Arial", 12), width=25)
        combo.grid(row=idx, column=2, padx=10, pady=5)
        combo.insert(0, "")  # Start with an empty value
        combo.set("")  # Keep combobox empty initially

        checkbox_var = tk.BooleanVar(value=states.get(header, {}).get("checked", False))  # Load saved state or default to False
        checkbox = tk.Checkbutton(left_frame, text="Lock", variable=checkbox_var, command=lambda h=header: toggle_lock(h), bg="#f9f9f9")
        checkbox.grid(row=idx, column=3, padx=10, pady=5)
        checkbox["state"] = "disabled"  # Initially disabled unless Admin is enabled

        # Synchronize combobox state with checkbox
        if checkbox_var.get():
            combo["state"] = "disabled"

        entry_widgets[header] = (combo, checkbox_var)
        checkboxes[header] = checkbox

    # Admin toggle button
    global admin_button
    admin_button = tk.Button(notes_button_frame, text="Enable Admin", command=toggle_admin, font=("Arial", 14), bg="#FFC107", width=15)
    admin_button.pack(side="right", padx=10, pady=5)

    # Save button
    tk.Button(notes_button_frame, text="SAVE", command=save_changes, font=("Arial", 14), bg="#4CAF50", fg="white", width=15).pack(side="right", padx=10, pady=5)

    edit_window.mainloop()


# Run the program
open_main_window()
