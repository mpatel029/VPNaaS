import json
import time
import sys
import select
import yaml
import random
import string

def main():
    while True:
        try:
            with open('tenant_database.yaml', 'r') as file:
                yaml_data = yaml.safe_load(file)
        except FileNotFoundError:
            print("Tenant database file not found.")
            return

        # Check for input or timeout
        print("Enter the Customer name (or 'quit' to exit): ", end='', flush=True)
        start_time = time.time()  # Start time for timeout
        key_name = ''  # Default empty key name
        while not select.select([sys.stdin], [], [], 0.1)[0] and (time.time() - start_time) < 180:
            pass  # Wait for input or timeout
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:  # If there's input available
            key_name = input()

        # Check if the user wants to quit
        if key_name.lower() == 'quit':
            break

        # Check if the key exists
        if key_name not in yaml_data:
            print("No customer entered.")
            continue

        vpc_info = get_vpc_info()
        save_to_yaml(key_name, vpc_info)

def get_vpc_info():
    vpc_info = {}

    num_vpcs = int(input("Enter the number of VPCs required: "))
    for vpc in range(1, num_vpcs + 1):
        num_vms = int(input(f"Enter the number of VMs in VPC {vpc}: "))
        vpc_info[f"{vpc}"] = num_vms

    return vpc_info

def save_to_yaml(key_name, data):
    try:
        with open('vpc_database.yaml', 'r') as yaml_file:
            existing_data = yaml.safe_load(yaml_file) or {}
    except FileNotFoundError:
        existing_data = {}

    # Generate unique random name for the customer
    random_name = ''.join(random.choices(string.ascii_lowercase, k=3))

    # Find the highest index for the current customer
    max_index = 0
    if key_name in existing_data:
        for name in existing_data[key_name]:
            index = int(name[-1])
            max_index = max(max_index, index)

    # Assign generated names to each VPC with incrementing numbers
    data_with_names = {}
    for idx, (name, num_vms) in enumerate(data.items(), start=1):
        new_name = f"{random_name}{idx + max_index}"
        data_with_names[new_name] = num_vms

    # Update existing_data with the new names
    existing_data[key_name] = data_with_names

    with open('vpc_database.yaml', 'w') as yaml_file:
        yaml.dump(existing_data, yaml_file, default_flow_style=False)
    print("Data saved to vpc_database.yaml successfully.")

if __name__ == "__main__":
    main()
