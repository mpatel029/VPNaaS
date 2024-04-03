import json
import time
import sys
import select

def main():
    while True:
        try:
            with open('tenant_database.json', 'r') as file:
                json_data = json.load(file)
        except FileNotFoundError:
            print("Tenant database file not found.")
            return
        
        # Display available customers
        print("Available Customers:")
        for key in json_data.keys():
            print("-", key)

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
        if key_name not in json_data:
            print("No customer entered.")
            continue
        
        vpc_info = get_vpc_info()
        save_to_json(key_name, vpc_info)

def get_vpc_info():
    vpc_info = {}
    
    num_vpcs = int(input("Enter the number of VPCs required: "))
    for vpc in range(1, num_vpcs + 1):
        num_vms = int(input(f"Enter the number of VMs in VPC {vpc}: "))
        vpc_info[f"{vpc}"] = num_vms
    
    return vpc_info

def save_to_json(key_name, data):
    try:
        with open('vpc_database.json', 'r') as json_file:
            existing_data = json.load(json_file)
    except FileNotFoundError:
        existing_data = {}
    
    existing_data[key_name] = data

    with open('vpc_database.json', 'w') as json_file:
        json.dump(existing_data, json_file, indent=4)
    print("Data saved to vpc_database.json successfully.")

if __name__ == "__main__":
    main()

