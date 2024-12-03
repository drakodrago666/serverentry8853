import tkinter as tk
from tkinter import messagebox
import requests
import pandas as pd
import time  # For simulating progress

# Flask API endpoint
FLASK_API_URL = "http://127.0.0.1:5000/search_by_po"

def search_po_numbers():
    """Search for rows by a list of P.O.# values and export them to Excel."""
    po_values = po_entry.get("1.0", "end").strip().split("\n")  # Get P.O.# values from the text box
    po_values = [po.strip() for po in po_values if po.strip()]  # Clean up input
    
    if not po_values:
        messagebox.showerror("Input Error", "Please enter at least one P.O.# value.")
        return

    results = []
    for po in po_values:
        try:
            response = requests.get(FLASK_API_URL, params={"po": po})
            if response.status_code == 200:
                data = response.json()
                results.extend(data)  # Add results to the list
            elif response.status_code == 404:
                results.append({"P.O.#": po, "Error": f"No data found for P.O.# {po}"})
            else:
                results.append({"P.O.#": po, "Error": f"Error fetching data for P.O.# {po}"})
        except requests.RequestException as e:
            results.append({"P.O.#": po, "Error": str(e)})
    
    if results:
        export_to_excel(results)

def export_to_excel(results):
    """Export results to an Excel file."""
    save_path = "search_results.xlsx"
    df = pd.DataFrame(results)
    try:
        df.to_excel(save_path, index=False, engine="openpyxl")
        messagebox.showinfo("Export Successful", f"Results exported to {save_path}.")
    except Exception as e:
        messagebox.showerror("Export Error", f"Failed to export results: {e}")

def show_splash_screen():
    """Display a splash screen while loading the main application."""
    splash = tk.Toplevel()
    splash.title("Loading")
    splash.geometry("300x150")
    splash.configure(bg="#333333")
    
    splash_label = tk.Label(
        splash, text="Initializing Application...\nPlease Wait.", bg="#333333",
        fg="white", font=("Arial", 12), pady=20
    )
    splash_label.pack(fill="both", expand=True)
    
    splash.update()  # Force update to display the splash screen
    time.sleep(2)  # Simulate loading delay
    splash.destroy()  # Close the splash screen

# Tkinter UI setup
root = tk.Tk()

# Call the splash screen before initializing the main window
root.withdraw()  # Hide the main window while the splash screen is visible
show_splash_screen()
root.deiconify()  # Show the main window after the splash screen is closed

root.title("P.O.# Search Tool")
root.geometry("500x400")
root.configure(bg="#f0f0f5")

# Header Label
header_label = tk.Label(
    root, text="P.O.# Search Tool", bg="#4CAF50", fg="white",
    font=("Arial", 16, "bold"), pady=10
)
header_label.pack(fill="x")

# Instructions
instruction_label = tk.Label(
    root, text="Enter P.O.# values (one per line):", bg="#f0f0f5",
    font=("Arial", 12)
)
instruction_label.pack(pady=10)

# Frame for text input and scrollbar
text_frame = tk.Frame(root)
text_frame.pack(fill="both", expand=True, padx=10, pady=5)

# Text box for P.O.# values
po_entry = tk.Text(text_frame, height=10, wrap="word", font=("Courier", 12))
po_entry.pack(side="left", fill="both", expand=True)

# Scrollbar for text box
text_scroll = tk.Scrollbar(text_frame, orient="vertical", command=po_entry.yview)
text_scroll.pack(side="right", fill="y")
po_entry.configure(yscrollcommand=text_scroll.set)

# Search button
search_button = tk.Button(
    root, text="Search and Export to Excel", bg="#4CAF50", fg="white",
    font=("Arial", 12, "bold"), command=search_po_numbers
)
search_button.pack(pady=10)

# Run the Tkinter app
root.mainloop()
