import yaml
from datetime import datetime

def main():
    try:
        with open('tenant_database.yaml', 'r') as file:
            data = yaml.safe_load(file)
            if data is None:
                data = {}
    except FileNotFoundError:
        data = {}

    tenant_ids = set(data.get('tenant_ids', []))  # To track tenant IDs

    # Generate next available tenant ID
    if tenant_ids:
        next_tenant_id = str(int(max(tenant_ids)) + 1)
    else:
        next_tenant_id = '1'

    # Take input from the user
    while True:
        key = input("Enter Tenant Name (or 'q' to quit): ").strip()
        if key.lower() == 'q':
            break

        # Add timestamp to the data
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data[key] = {"Tenant-ID": next_tenant_id, "Timestamp": timestamp}

        # Update tenant_ids
        tenant_ids.add(next_tenant_id)

        # Generate next available tenant ID
        next_tenant_id = str(int(next_tenant_id) + 1)

    # Update the tenant_ids in the data
    data['tenant_ids'] = list(tenant_ids)

    # Write the updated data to tenant_database.json
    filename = 'tenant_database.yaml'
    with open(filename, 'w') as file:
        yaml.dump(data, file, indent=4)

    print("Data has been stored to", filename)

if __name__ == "__main__":
    main()
