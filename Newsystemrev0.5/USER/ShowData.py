import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import requests
import os

# Define the Flask server endpoints
SERVER_URL = "http://127.0.0.1:5000"
GET_DATA_URL = f"{SERVER_URL}/get_data"
LIST_HEADERS_URL = f"{SERVER_URL}/list_headers"
REFINED_DIR = os.path.join("DB", "refined")  # Directory for refined .txt files

# Sanitize header names by replacing spaces, slashes, and dots with underscores
def sanitize_header_name(header):
    return header.replace(" ", "_").replace("/", "_").replace(".", "_")

# Ensure .txt files for headers exist
def ensure_refined_files(headers):
    if not os.path.exists(REFINED_DIR):
        os.makedirs(REFINED_DIR)  # Create the refined directory if it doesn't exist
    for header in headers:
        sanitized_header = sanitize_header_name(header)
        file_path = os.path.join(REFINED_DIR, f"{sanitized_header}.txt")

        # Only create new files and print a message if the file does not exist
        if not os.path.exists(file_path):
            with open(file_path, "w") as file:
                file.write("")  # Create an empty file
            print(f"Creating new file: {file_path}")  # Print only when creating a new file

# Load data from the Flask server
def load_data():
    try:
        response = requests.get(GET_DATA_URL)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            return df
        else:
            messagebox.showerror("Error", f"Failed to fetch data: {response.json().get('message')}")
            return pd.DataFrame()
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Could not connect to the server: {e}")
        return pd.DataFrame()

# Get headers from the Flask server
def get_headers():
    try:
        response = requests.get(LIST_HEADERS_URL)
        if response.status_code == 200:
            return response.json().get("headers", [])
        else:
            messagebox.showerror("Error", f"Failed to fetch headers: {response.json().get('message')}")
            return []
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Could not connect to the server: {e}")
        return []

# Populate Treeview with DataFrame data
def populate_treeview(tree, df):
    # Clear any existing data
    tree.delete(*tree.get_children())
    
    # Set columns and auto-size based on content
    tree["columns"] = list(df.columns)
    tree["show"] = "headings"  # Hide row indices
    
    # Configure columns with fixed width and stretching
    for column in df.columns:
        tree.heading(column, text=column)
        tree.column(column, anchor="center", width=150)  # Fixed width

    # Add rows to the treeview
    for _, row in df.iterrows():
        tree.insert("", "end", values=list(row))

# Filter DataFrame based on search query and column filters
def filter_data(tree, df, search_query, column_filters):
    filtered_df = df

    # Apply search query filter if any
    if search_query:
        filtered_df = filtered_df[filtered_df.apply(
            lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]

    # Apply column filters on top of the search filter
    for column, value in column_filters.items():
        if value:
            filtered_df = filtered_df[filtered_df[column].astype(str).str.contains(value, case=False, na=False)]
    
    populate_treeview(tree, filtered_df)

# Open column filter window with dropdowns
def open_column_filter_window(root, tree, df, filters, search_var):
    def apply_filters():
        # Get the current search query
        search_query = search_var.get()

        # Update column filters with user inputs
        column_filters = {col: var.get() for col, var in column_vars.items()}

        # Combine existing filters with the new ones
        current_filters = filters.copy()  # Copy the existing filters
        current_filters.update(column_filters)  # Update with the new column filters
        
        # Apply the combined filters
        filter_data(tree, df, search_query, current_filters)
        filter_window.destroy()

    filter_window = tk.Toplevel(root)
    filter_window.title("Filter by Column")

    column_vars = {}
    for idx, column in enumerate(df.columns):
        # Create label and dropdown for each column
        label = tk.Label(filter_window, text=column)
        label.grid(row=idx, column=0, padx=5, pady=5, sticky="w")
        
        var = tk.StringVar(value="")  # Set the default value to an empty string
        column_vars[column] = var
        
        # Create a dropdown box for each column with unique values from the column
        unique_values = df[column].dropna().unique().tolist()
        dropdown = ttk.Combobox(filter_window, textvariable=var, values=[""] + unique_values, width=30)  # Add an empty string to the values
        dropdown.grid(row=idx, column=1, padx=5, pady=5)

    # Apply button
    apply_button = tk.Button(filter_window, text="Apply Filters", command=apply_filters)
    apply_button.grid(row=len(df.columns), column=0, columnspan=2, pady=10)

# Clear all filters and reset the treeview
def clear_filters(tree, df, search_var, filters):
    # Clear search entry and column filters
    search_var.set("")
    for var in filters.values():
        var.set("")  # Reset all column filters
    
    # Reset the DataFrame and reload the original data
    populate_treeview(tree, df)

# Main GUI
def main():
    root = tk.Tk()
    root.title("Excel Data Viewer")
    root.geometry("1200x800")  # Set initial window size

    # Load data and headers from the Flask server
    headers = get_headers()
    df = load_data()

    if not df.empty:
        # Ensure .txt files for headers exist
        ensure_refined_files(headers)

        # Initialize filters dictionary to store the column filters
        filters = {}

        # Create a Frame for the search bar and Treeview
        frame = tk.Frame(root)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Search Bar
        search_frame = tk.Frame(frame)
        search_frame.pack(fill="x", pady=5)
        tk.Label(search_frame, text="Search:").pack(side="left", padx=5)
        search_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=search_var, width=30).pack(side="left", padx=5)
        tk.Button(search_frame, text="Search", command=lambda: filter_data(tree, df, search_var.get(), filters)).pack(side="left", padx=5)
        tk.Button(search_frame, text="Filter by Column", command=lambda: open_column_filter_window(root, tree, df, filters, search_var)).pack(side="left", padx=5)
        tk.Button(search_frame, text="Clear Filters", command=lambda: clear_filters(tree, df, search_var, filters)).pack(side="left", padx=5)

        # Treeview Frame
        tree_frame = tk.Frame(frame)
        tree_frame.pack(fill="both", expand=True)

        # Treeview to display data
        tree = ttk.Treeview(tree_frame, show="headings")
        tree.pack(side="left", fill="both", expand=True)

        # Scrollbars for Treeview
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        vsb.pack(side="right", fill="y")
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        hsb.pack(side="bottom", fill="x")

        # Configure treeview to work with scrollbars
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Populate Treeview with initial data
        populate_treeview(tree, df)

        root.mainloop()

if __name__ == "__main__":
    main()
