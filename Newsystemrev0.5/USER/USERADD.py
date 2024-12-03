import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import requests
import os
import json
from tkcalendar import Calendar

# Define paths
base_dir = os.path.dirname(os.path.abspath(__file__))  # Get the program's directory
state_file_path = os.path.join(base_dir, "DB", "settings", "combobox_states2.json")  # JSON file to save field states
visual_settings_file = os.path.join(base_dir, "visual_settings.json")  # Visual settings file
refined_dir = os.path.join(base_dir, "Db", "refined")  # Directory for refined .txt files

# Flask server endpoint
FLASK_SERVER = "http://localhost:5000"

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

# Ensure the directory and the state file exists
def ensure_directory_exists():
    directory = os.path.dirname(state_file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    if not os.path.exists(state_file_path):
        with open(state_file_path, 'w') as file:
            json.dump({}, file)

# Load visual settings
def load_visual_settings():
    default_settings = {
        "font_family": "Arial",
        "font_size": 12,
        "bg_color": "#ffffff",
        "fg_color": "#000000",
        "button_bg_color": "#f0f0f0",
        "button_fg_color": "#000000"
    }
    try:
        if os.path.exists(visual_settings_file):
            with open(visual_settings_file, "r") as file:
                settings = json.load(file)
                for key, value in default_settings.items():
                    settings.setdefault(key, value)
                return settings
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load visual settings: {e}")
    return default_settings

# Load saved field states
def load_field_states():
    ensure_directory_exists()  # Ensure the directory and file exist before loading
    with open(state_file_path, 'r') as file:
        return json.load(file)

# Save field states to file
def save_field_states(states):
    ensure_directory_exists()  # Ensure the directory and file exist before saving
    with open(state_file_path, 'w') as file:
        json.dump(states, file)

# Sanitize header names by replacing spaces, slashes, and dots with underscores
def sanitize_header_name(header):
    return header.replace(" ", "_").replace("/", "_").replace(".", "_")

# Download refined files from the server
def download_refined_files():
    """Download refined files from the Flask server."""
    try:
        response = requests.get(f"{FLASK_SERVER}/list_refined")
        if response.status_code == 200:
            refined_files = response.json().get("files", {})
            if not os.path.exists(refined_dir):
                os.makedirs(refined_dir)  # Ensure the directory exists

            # Download and save each refined file
            for file_name, content in refined_files.items():
                file_path = os.path.join(refined_dir, file_name)
                with open(file_path, "w") as file:
                    file.write("\n".join(content))
                print(f"Downloaded refined file: {file_path}")
        else:
            messagebox.showerror("Error", f"Failed to fetch refined files: {response.json().get('message')}")
    except Exception as e:
        messagebox.showerror("Error", f"Could not connect to server: {e}")

# Load suggestions for a header
def load_suggestions(header):
    sanitized_header = sanitize_header_name(header)
    file_path = os.path.join(refined_dir, f"{sanitized_header}.txt")
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return [line.strip() for line in file if line.strip()]
    return []

# Save a new entry to the .txt file if it doesn't already exist
def save_suggestion(header, value):
    sanitized_header = sanitize_header_name(header)
    file_path = os.path.join(refined_dir, f"{sanitized_header}.txt")
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            lines = [line.strip() for line in file if line.strip()]
        if value not in lines:
            with open(file_path, "a") as file:
                file.write(f"{value}\n")

# Fetch headers from the Flask server
def fetch_headers_from_server():
    try:
        response = requests.get(f"{FLASK_SERVER}/get_data")
        if response.status_code == 200:
            data = response.json()
            if data:
                return list(data[0].keys())  # Get headers from the first row of data
        else:
            messagebox.showerror("Error", f"Failed to fetch headers: {response.json().get('message')}")
            return []
    except Exception as e:
        messagebox.showerror("Error", f"Could not connect to server: {e}")
        return []

# Submit a new entry to the Flask server
def submit_new_entry(entry_data):
    try:
        response = requests.post(f"{FLASK_SERVER}/submit_data", json=entry_data)
        if response.status_code == 200:
            messagebox.showinfo("Success", "New entry submitted successfully.")
        else:
            messagebox.showerror("Error", f"Failed to submit data: {response.json().get('message')}")
    except Exception as e:
        messagebox.showerror("Error", f"Could not connect to server: {e}")

# Main UI setup
# Main UI setup
def setup_ui(headers):
    global admin_mode_active, checkboxes, field_states, notes_text, description_text

    root = tk.Tk()
    root.title("Add New Data Entry")
    visual_settings = load_visual_settings()
    root.configure(bg=visual_settings["bg_color"])
    root.geometry("1200x700")

    admin_mode_active = tk.BooleanVar(value=False)
    field_states = load_field_states()
    checkboxes = {}

    # Download refined files from the server
    download_refined_files()

    # Adding "Unit" to the list of headers if it doesn't already exist
    if "Unit" not in headers:
        headers.append("Unit")

    def toggle_lock(field, is_locked):
        """Enable or disable a field based on the checkbox."""
        if is_locked:
            field.config(state="disabled")
        else:
            field.config(state="normal")

    tk.Label(root, text="Add New Entry", bg=visual_settings["bg_color"], fg=visual_settings["fg_color"],
             font=(visual_settings["font_family"], visual_settings["font_size"], "bold")).grid(row=0, column=0, columnspan=2, pady=10, sticky="w")

    left_frame = tk.Frame(root, bg=visual_settings["bg_color"])
    left_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nw")

    right_frame = tk.Frame(root, bg=visual_settings["bg_color"])
    right_frame.grid(row=1, column=1, padx=10, pady=10, sticky="ne")

    row_left, col_left = 0, 0
    entry_fields = {}

    headers_left = [header for header in headers if header != "NOTES" and header != "Description"]
    split_point = len(headers_left) // 2

    for idx, header in enumerate(headers_left):
        if idx == split_point:
            row_left = 0
            col_left += 3

        tk.Label(left_frame, text=header, bg=visual_settings["bg_color"], fg=visual_settings["fg_color"],
                 font=(visual_settings["font_family"], visual_settings["font_size"])).grid(row=row_left, column=col_left, padx=5, pady=5, sticky="w")

        if "Date" in header:
            cal_button = tk.Button(left_frame, text="Cal", font=(visual_settings["font_family"], visual_settings["font_size"]),
                                   command=lambda header=header: open_calendar(header))
            cal_button.grid(row=row_left, column=col_left + 1, padx=5, pady=5, sticky="ew")
            entry_fields[header] = cal_button
        else:
            combo = ttk.Combobox(left_frame, font=(visual_settings["font_family"], visual_settings["font_size"]))
            combo.grid(row=row_left, column=col_left + 1, padx=5, pady=5, sticky="ew")
            suggestions = load_suggestions(header)
            combo["values"] = suggestions
            entry_fields[header] = combo

        is_locked = bool(field_states.get(header, False))
        field_lock_var = tk.BooleanVar(value=is_locked)
        checkboxes[header] = {"var": field_lock_var, "checkbox": None}

        field_lock_checkbox = tk.Checkbutton(
            left_frame, text="Lock", variable=field_lock_var,
            command=lambda header=header, f=entry_fields.get(header, None): toggle_lock(f, checkboxes[header]["var"].get()),
            bg=visual_settings["bg_color"], fg=visual_settings["fg_color"],
            font=(visual_settings["font_family"], visual_settings["font_size"])
        )
        field_lock_checkbox.grid(row=row_left, column=col_left + 2, padx=5, pady=5)
        checkboxes[header]["checkbox"] = field_lock_checkbox

        toggle_lock(entry_fields.get(header, None), is_locked)
        field_lock_checkbox.config(state="disabled")
        row_left += 1

    # Adding "NOTES" field
    tk.Label(right_frame, text="NOTES", bg=visual_settings["bg_color"], fg=visual_settings["fg_color"],
             font=(visual_settings["font_family"], visual_settings["font_size"])).grid(row=0, column=0, padx=5, pady=5, sticky="nw")
    notes_text = tk.Text(right_frame, height=20, width=50, font=(visual_settings["font_family"], visual_settings["font_size"]))
    notes_text.grid(row=1, column=0, padx=5, pady=5, sticky="nw")
    entry_fields["NOTES"] = notes_text

    # Adding "DESCRIPTION:" field
    tk.Label(right_frame, text="Description", bg=visual_settings["bg_color"], fg=visual_settings["fg_color"],
             font=(visual_settings["font_family"], visual_settings["font_size"])).grid(row=2, column=0, padx=5, pady=5, sticky="nw")
    description_text = tk.Text(right_frame, height=20, width=50, font=(visual_settings["font_family"], visual_settings["font_size"]))
    description_text.grid(row=3, column=0, padx=5, pady=5, sticky="nw")
    entry_fields["Description"] = description_text

    def open_calendar(header):
        def on_date_selected(date):
            entry_fields[header].config(text=date)  # Update the button text with the selected date
            top.destroy()

        top = tk.Toplevel(root)
        top.title(f"Select Date for {header}")

        cal = Calendar(top, selectmode='day', date_pattern='yyyy-mm-dd')
        cal.pack(pady=20)
        cal_button = tk.Button(top, text="Select", command=lambda: on_date_selected(cal.get_date()))
        cal_button.pack()

    def toggle_admin_mode():
        if admin_mode_active.get():
            admin_mode_active.set(False)
            for checkbox_info in checkboxes.values():
                checkbox_info["checkbox"].config(state="disabled")
            messagebox.showinfo("Admin Mode", "Admin mode disabled.")
        else:
            password = simpledialog.askstring("Admin Access", "Enter Admin Password:", show="*")
            if password == "8853":
                admin_mode_active.set(True)
                for checkbox_info in checkboxes.values():
                    checkbox_info["checkbox"].config(state="normal")
                messagebox.showinfo("Admin Mode", "Admin mode enabled.")
            else:
                messagebox.showerror("Error", "Incorrect password.")

    def save_entry():
        entry_data = {}
        for header, field in entry_fields.items():
            if isinstance(field, tk.Text):
                entry_data[header] = field.get("1.0", tk.END).strip()
            else:
                if isinstance(field, tk.Button):  # Update the date button's text
                    entry_data[header] = field.cget("text").strip()
                else:
                    entry_data[header] = field.get().strip()
                save_suggestion(header, entry_data[header])

        for header, lock_info in checkboxes.items():
            field_states[header] = lock_info["var"].get()
        save_field_states(field_states)

        submit_new_entry(entry_data)

        for widget in entry_fields.values():
            if isinstance(widget, tk.Text):
                widget.delete("1.0", tk.END)
            elif isinstance(widget, tk.Button):  # Reset the date button's text
                widget.config(text="Cal")
            else:
                widget.set("")

        messagebox.showinfo("Success", "Entry submitted and fields cleared.")

    tk.Button(root, text="Save Entry", command=save_entry, bg=visual_settings["button_bg_color"], fg=visual_settings["button_fg_color"],
              font=(visual_settings["font_family"], visual_settings["font_size"])).grid(row=2, column=0, pady=20, sticky="w")

    tk.Button(root, text="Toggle Admin", command=toggle_admin_mode, bg=visual_settings["button_bg_color"], fg=visual_settings["button_fg_color"],
              font=(visual_settings["font_family"], visual_settings["font_size"])).grid(row=2, column=1, pady=20, sticky="w")

    root.mainloop()

headers = fetch_headers_from_server()
if headers:
    setup_ui(headers)
