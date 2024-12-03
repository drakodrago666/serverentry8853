import random
import pandas as pd
from faker import Faker
from datetime import timedelta
import os

# Initialize Faker to generate random names and addresses
fake = Faker()

# List of possible machine types from the given tube_bender_models variable
tube_bender_models = [
    "eMOB 52 2 Bend", "eMOB 63 2 Bend", "eMOB 80 2 Bend", "MDH 60", "MDH 90", "MDH 120",
    "CH 50", "CH 100", "CH 150", "E-TURN 52", "E-TURN 63", "E-TURN 80", "ELECT40", "ELECT52",
    "ELECT63", "SMART 28", "SMART 42", "SMART 63", "SRB 60", "SRB 80", "SRB 100", "HMT 50",
    "HMT 80", "HMT 120", "HBS 50", "HBS 80", "HBS 120", "VB19", "VB25", "VB42", "VB65", "VB90",
    "3D 50", "3D 80", "3D 120", "CNC 50", "CNC 80", "CNC 120", "LS-150", "LS-200", "LS-250", "LS-300",
    "LS-400", "LS-500", "LS-600", "LS-700", "LS-800", "LS-900", "EL-10", "EL-20", "EL-30", "EL-40",
    "EL-50", "EL-60", "EL-70", "EL-80", "EL-90", "EL-100", "LC-100", "LC-120", "LC-150", "LC-180",
    "LC-200", "LC-250", "LC-300", "LC-400", "LC-500", "LC-600", "LC-700", "LC-800", "LC-900", "LC-1000",
    "LC-1200", "HS-120", "HS-140", "HS-160", "HS-180", "HS-200", "HS-250", "HS-300", "HS-350", "HS-400",
    "HS-450", "CS-50", "CS-100", "CS-150", "CS-200", "CS-250", "CS-300", "CS-350", "CS-400", "CS-500",
    "CS-600", "CS-700", "CS-800", "CS-900", "CS-1000", "CS-1200", "LS-3000", "LS-3500", "LS-4000", "LS-4500",
    "LS-5000", "RS-50", "RS-100", "RS-150", "RS-200", "RS-250", "RS-300", "RS-350", "RS-400", "RS-500",
    "RS-600", "RS-700", "RS-800", "RS-900", "RS-1000", "RS-1100", "TS-100", "TS-150", "TS-200", "TS-250",
    "TS-300", "TS-350", "TS-400", "TS-500", "TS-600", "TS-700", "TS-800", "TS-900", "TS-1000", "TS-1200",
    "TS-1500", "VS-100", "VS-200", "VS-300", "VS-400", "VS-500", "VS-600", "VS-700", "VS-800", "VS-900",
    "VS-1000", "VS-1100", "VS-1200", "VS-1300", "VS-1400", "VS-1500", "ZS-100", "ZS-150", "ZS-200", "ZS-250",
    "ZS-300", "ZS-350", "ZS-400", "ZS-450", "ZS-500", "ZS-600"
]

# Tooling types list
tooling_types = [
    "BEND DIE", "CLAMP DIE", "BEND DIE INSERT", "PRESSURE DIE", "WIPER INSERT",
    "SQUAREBACK WIPER", "COLLET", "COLLET PADS", "MASTER COLLER", "MANDREL ASSEMBLY",
    "MANDREL BALL", "MANDREL SHANK"
]

# Function to generate a single row of example data with intelligent logic
def generate_example_data(customer_dict):
    # Random data generation for each field
    customer_name = fake.company()
    contact_name = fake.name()

    # Create unique S.O.# based on customer
    so_number = f"{random.randint(10000, 99999)}"

    # Create dynamic Dwg. based on first 3 letters of customer
    dwg_prefix = customer_name[:3].upper()
    dwg = f"{dwg_prefix} - {random.randint(1, 99999):05d} - 01"

    # Ensure unique REP initials based on contact name
    rep_initials = "".join([word[0].upper() for word in contact_name.split()[:3]])

    # Use customer name as the unique identifier for customer number
    customer_number = str(abs(hash(customer_name)) % (10**10))

    # Create a unique key for the customer
    if customer_number not in customer_dict:
        customer_dict[customer_number] = customer_name

    # Other fields
    po_number = f"{random.randint(1000000000, 9999999999)}"
    
    # Quantity logic: Mostly 1-99, rarely 3 digits
    quantity = random.randint(1, 99)
    if random.random() < 0.05:  # 5% chance of getting 3 digits
        quantity = random.randint(100, 999)
    
    description = "Description of part and usage"
    cost_each = random.uniform(50, 500)

    # Generate random project complexity to influence dates
    project_complexity = random.choice(['simple', 'medium', 'complex'])

    # Start Date
    start_date = fake.date_this_year()

    # Due Date, based on project complexity
    if project_complexity == 'simple':
        due_date = start_date + timedelta(days=random.randint(1, 7))
    elif project_complexity == 'medium':
        due_date = start_date + timedelta(days=random.randint(7, 14))
    else:
        due_date = start_date + timedelta(days=random.randint(14, 30))

    # Completion Date, it should be between start and due date
    completion_date = start_date + timedelta(days=random.randint(1, (due_date - start_date).days))

    # Engineer Start Date and Released Date logic
    engineer_start_date = start_date + timedelta(days=random.randint(1, 7))
    released_date = engineer_start_date + timedelta(days=random.randint(1, 7))

    total_dollars = cost_each * quantity
    notes = fake.text()
    received_in_engineering = fake.date_this_year()

    status = "not started"

    # Determine status based on dates
    if completion_date < due_date:
        status = "completed"
    elif due_date - start_date < timedelta(days=7):
        status = "help needed"
    else:
        status = "in progress"

    # Randomly choose machine type and tooling type from the provided lists
    machine_type = random.choice(tube_bender_models)

    # Randomly select between 1 to 5 tooling types
    num_tooling_types = random.randint(1, 5)
    selected_tooling_types = random.sample(tooling_types, num_tooling_types)
    tooling_type = ", ".join(selected_tooling_types)
    
    # Random values for tube O.D., C.L.R., W.T., and unit type
    tube_od = random.uniform(0.1, 10.0)
    tube_clr = random.uniform(0.05, 5.0)
    tube_wt = random.uniform(0.01, 2.0)
    unit = random.choice(["imperial", "metric"])

    # Convert dates to string format
    start_date = start_date.strftime("%m-%d-%Y")
    due_date = due_date.strftime("%m-%d-%Y")
    completion_date = completion_date.strftime("%m-%d-%Y")
    engineer_start_date = engineer_start_date.strftime("%m-%d-%Y")
    released_date = released_date.strftime("%m-%d-%Y")
    received_in_engineering = received_in_engineering.strftime("%m-%d-%Y")

    # Construct the row as a dictionary
    row = {
        "S.O.#": so_number,
        "Dwg.": dwg,
        "REP": rep_initials,
        "Customer": customer_name,
        "Contact": contact_name,
        "P.O.#": po_number,
        "Quantity": quantity,
        "Description": description,
        "Cost Each": cost_each,
        "Start Date": start_date,
        "Due Date": due_date,
        "Completion Date": completion_date,
        "Total $'s": total_dollars,
        "NOTES": notes,
        "Received in Engineering": received_in_engineering,
        "Engineer Start Date": engineer_start_date,
        "Released Date": released_date,
        "Customer Number": customer_number,
        "Status": status,
        "machine type": machine_type,
        "Tooling type": tooling_type,
        "Tube O.D.": tube_od,
        "Tube C.L.R.": tube_clr,
        "Tube W.T.": tube_wt,
        "Unit": unit
    }

    return row

# Function to generate multiple rows of example data with intelligent logic
def generate_excel_data(num_rows):
    data = []
    customer_dict = {}  # To keep track of unique customers and their numbers
    for _ in range(num_rows):
        data.append(generate_example_data(customer_dict))
    
    # Convert the data to a DataFrame
    df = pd.DataFrame(data)
    
    # Define column types (for columns that are already strings, we specify their type as string)
    df["S.O.#"] = df["S.O.#"].astype(str)
    df["Dwg."] = df["Dwg."].astype(str)
    df["REP"] = df["REP"].astype(str)
    df["Customer"] = df["Customer"].astype(str)
    df["Contact"] = df["Contact"].astype(str)
    df["P.O.#"] = df["P.O.#"].astype(str)
    df["Quantity"] = df["Quantity"].astype(int)
    df["Description"] = df["Description"].astype(str)
    df["Cost Each"] = df["Cost Each"].astype(float)
    df["Total $'s"] = df["Total $'s"].astype(float)
    df["NOTES"] = df["NOTES"].astype(str)
    df["Customer Number"] = df["Customer Number"].astype(str)
    df["Status"] = df["Status"].astype(str)
    df["machine type"] = df["machine type"].astype(str)
    df["Tooling type"] = df["Tooling type"].astype(str)
    df["Tube O.D."] = df["Tube O.D."].astype(float)
    df["Tube C.L.R."] = df["Tube C.L.R."].astype(float)
    df["Tube W.T."] = df["Tube W.T."].astype(float)
    df["Unit"] = df["Unit"].astype(str)
    
    # Save the DataFrame to an Excel file, replacing the existing file "aggregated_data2.xlsx"
    current_directory = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(current_directory, "aggregated_data2.xlsx")
    df.to_excel(file_path, index=False)

# Prompt the user for the number of rows to generate
num_rows = int(input("Enter the number of rows to generate: "))
generate_excel_data(num_rows)
print(f"Excel file with {num_rows} rows of data generated successfully and saved as aggregated_data2.xlsx!")
