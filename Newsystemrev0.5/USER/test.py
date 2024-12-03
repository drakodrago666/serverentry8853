import os
import json
import requests

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
