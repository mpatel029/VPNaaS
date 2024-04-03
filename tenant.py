import json
from datetime import datetime

def main():
    try:
        with open('tenant_database.json', 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}

    tenant_ids = set(data.get('tenant_ids', []))  # To track tenant IDs
    
    # Take input from the user
    while True:
        key = input("Enter Tenant Name (or 'q' to quit): ")
        if key.lower() == 'q':
            break
        
        # Check if the tenant ID already exists or not unique
        while True:
            value = input("Enter Tenant ID for {}: ".format(key))
            if value not in tenant_ids:
                tenant_ids.add(value)
                break
            else:
                print("Tenant ID '{}' already exists or is not unique. Please enter a different ID.".format(value))
        
        # Add timestamp to the data
        timestamp = datetime.now().isoformat()
        data[key] = {"Tenant ID": value, "Timestamp": timestamp}
    
    # Update the tenant_ids in the data
    data['tenant_ids'] = list(tenant_ids)
    
    # Write the updated data to tenant_database.json
    filename = 'tenant_database.json'
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)
    
    print("JSON data has been appended to", filename) 

if __name__ == "__main__":
        main()

