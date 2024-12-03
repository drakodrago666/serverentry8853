# standalone_server.py
from flask import Flask, request, jsonify
import pandas as pd
import os
import logging
from colorama import Fore, Style, init

# Initialize colorama for colored output
init(autoreset=True)

# Paths and configuration
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Base directory of the script
DB_DIR = os.path.join(BASE_DIR, "DB")  # Directory for DB
EXCEL_FILE_PATH = os.path.join(DB_DIR, "aggregated_data2.xlsx")  # Path for the Excel file
REFINED_DIR = os.path.join(DB_DIR, "refined")  # Directory for refined files

# Predefined headers for the Excel file
DEFAULT_HEADERS = [
    "S.O.#", "Dwg.", "REP", "Customer", "Contact", "P.O.#", "Quantity", 
    "Description", "Cost Each", "Start Date", "Due Date", "Completion Date", 
    "Total $'s", "NOTES", "Received in Engineering", "Engineer Start Date", 
    "Released Date", "Customer Number", "Engineer Status", "machine type", 
    "Tooling type", "Tube O.D.", "Tube C.L.R.", "Tube W.T.", "Unit"
]

# Ensure necessary directories exist
os.makedirs(DB_DIR, exist_ok=True)
os.makedirs(REFINED_DIR, exist_ok=True)

# Set up logging
LOG_FILE_PATH = os.path.join(BASE_DIR, "server_log.txt")
logging.basicConfig(
    filename=LOG_FILE_PATH,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

app = Flask(__name__)

def log_and_print(message, color=Fore.RESET, level="info"):
    """Log the message and print it to the console with color."""
    if level == "info":
        logging.info(message)
    elif level == "warning":
        logging.warning(message)
    elif level == "error":
        logging.error(message)

    print(color + message + Style.RESET_ALL)

def ensure_excel_file():
    """Ensure the Excel file exists with the predefined headers."""
    if not os.path.exists(EXCEL_FILE_PATH):
        log_and_print("Excel file not found. Creating a new file with default headers...", color=Fore.YELLOW)
        df = pd.DataFrame(columns=DEFAULT_HEADERS)  # Create an empty DataFrame with default headers
        df.to_excel(EXCEL_FILE_PATH, index=False, engine="openpyxl")
        log_and_print(f"Excel file created at: {EXCEL_FILE_PATH}", color=Fore.GREEN)
    else:
        log_and_print("Excel file already exists.", color=Fore.CYAN)

def ensure_txt_files_and_sync(headers, df):
    """Ensure a .txt file exists for each header and synchronize its contents."""
    for header in headers:
        sanitized_header = header.replace(" ", "_").replace("/", "_").replace(".", "_")
        file_path = os.path.join(REFINED_DIR, f"{sanitized_header}.txt")

        # Extract unique values for this column
        column_values = df[header].dropna().unique().astype(str).tolist()

        if not os.path.exists(file_path):
            log_and_print(f"Creating new file: {file_path}", color=Fore.YELLOW)
            with open(file_path, "w") as file:
                file.write("\n".join(column_values))
        else:
            log_and_print(f"File exists: {file_path}. Updating...", color=Fore.CYAN)
            with open(file_path, "r") as file:
                existing_values = {line.strip() for line in file if line.strip()}
            
            updated_values = sorted(existing_values.union(column_values))
            
            with open(file_path, "w") as file:
                file.write("\n".join(updated_values))

            log_and_print(f"Updated file: {file_path} with {len(updated_values)} values", color=Fore.GREEN)

def initialize_files():
    """Check the Excel file, create .txt files for each header, and sanitize them."""
    log_and_print("Initializing files...", color=Fore.BLUE)
    ensure_excel_file()  # Ensure the Excel file exists
    df = pd.read_excel(EXCEL_FILE_PATH)
    headers = list(df.columns)
    ensure_txt_files_and_sync(headers, df)
    log_and_print("File initialization complete.", color=Fore.GREEN)

# Initialize files before the server starts
initialize_files()

@app.route('/search_by_po', methods=['GET'])
def search_by_po():
    """Search for a row by P.O.#."""
    po_number = request.args.get('po')
    if not po_number:
        log_and_print("Search by P.O.# failed: Missing 'po' parameter.", color=Fore.RED)
        return jsonify({"message": "P.O.# parameter is required"}), 400

    if not os.path.exists(EXCEL_FILE_PATH):
        log_and_print("Search by P.O.# failed: Excel file not found.", color=Fore.RED)
        return jsonify({"message": "Excel file not found"}), 404

    try:
        log_and_print(f"Searching for P.O.#: {po_number}", color=Fore.BLUE)
        # Load the Excel file
        df = pd.read_excel(EXCEL_FILE_PATH)

        # Ensure the P.O.# column exists
        if "P.O.#" not in df.columns:
            log_and_print("P.O.# column not found in Excel file.", color=Fore.RED)
            return jsonify({"message": "P.O.# column not found in the Excel file"}), 400

        # Convert P.O.# column to string and search input as string
        df["P.O.#"] = df["P.O.#"].astype(str)
        po_number = str(po_number)

        # Perform the search
        matching_rows = df[df["P.O.#"] == po_number]
        if matching_rows.empty:
            log_and_print(f"No rows found for P.O.# {po_number}.", color=Fore.YELLOW)
            return jsonify({"message": f"No rows found for P.O.# {po_number}"}), 404

        log_and_print(f"Found rows for P.O.# {po_number}. Returning results.", color=Fore.GREEN)
        return jsonify(matching_rows.to_dict(orient="records")), 200
    except Exception as e:
        log_and_print(f"An error occurred while searching for P.O.# {po_number}: {str(e)}", color=Fore.RED, level="error")
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500

@app.route('/list_headers', methods=['GET'])
def list_headers():
    """List all headers in the Excel file."""
    if not os.path.exists(EXCEL_FILE_PATH):
        log_and_print("Header listing failed: Excel file not found.", color=Fore.RED)
        return jsonify({"message": "No Excel file found"}), 404

    df = pd.read_excel(EXCEL_FILE_PATH)
    headers = list(df.columns)
    log_and_print("Headers listed successfully.", color=Fore.GREEN)
    return jsonify({"headers": headers}), 200

@app.route('/sync_refined', methods=['POST'])
def sync_refined():
    """Synchronize refined files and their contents."""
    try:
        log_and_print("Synchronizing refined files...", color=Fore.BLUE)
        df = pd.read_excel(EXCEL_FILE_PATH)
        headers = list(df.columns)
        ensure_txt_files_and_sync(headers, df)
        log_and_print("Refined files synchronized successfully.", color=Fore.GREEN)
        return jsonify({"message": "Refined files synchronized successfully."}), 200
    except Exception as e:
        log_and_print(f"An error occurred during synchronization: {str(e)}", color=Fore.RED, level="error")
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500

# Add similar log_and_print calls to all other routes for consistent visibility

if __name__ == '__main__':
    log_and_print("Starting the Flask server on http://0.0.0.0:5000", color=Fore.MAGENTA)
    app.run(host="0.0.0.0", port=5000)
