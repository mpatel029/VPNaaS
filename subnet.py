import yaml
import ipaddress

vm_counter = 1

def check_subnet_overlap(subnet, existing_subnets, vpc_id):
    try:
        subnet_network = ipaddress.IPv4Network(subnet)
    except ValueError:
        print(f"Invalid subnet format: {subnet}")
        return True

    if vpc_id in existing_subnets:
        for existing_subnet in existing_subnets[vpc_id]:
            existing_network = ipaddress.IPv4Network(existing_subnet)
            if subnet_network.overlaps(existing_network):
                return True
    return False

def calculate_subnet_range(subnet):
    network = ipaddress.IPv4Network(subnet)
    return str(network.network_address + 3), str(network.broadcast_address - 1)

def get_user_input(tenant, vpc_name, num_vms, existing_subnets):
    global vm_counter
    vm_configurations = []
    print("Configuring for {} VPC {}".format(tenant, vpc_name))
    for i in range(1, num_vms + 1):
        print(f"Configuring VM {i}")
        vm_name = f"vm{vm_counter}"
        vm_counter += 1
        hostname = input(f"Enter the name for VM {i}: ")
        vcpus = 1
        while True:
            try:
                vcpus = int(input("Enter number of vCPUs: "))
            except Exception as e:
                print("Invalid number.")
                continue
            if vcpus < 1 or vcpus > 16:
                print("Please enter a number between 1 and 16.")
                continue
            else:
                break
        memory = 1048
        while True:
            try:
                memory = int(input("Enter memory size (in MB): "))
            except Exception as e:
                print("Invalid memory size.")
                continue
            if memory < 256 or memory > 16384:
                print("Please enter a number between 256 and 16384.")
                continue
            else:
                break
        disk_size = "10G"
        while True:
            disk_size = input("Enter disk size (e.g., 10G): ")
            if not disk_size.endswith("G"):
                print("Disk size must end with G.")
                continue
            disk_size_int = 0
            try:
                disk_size_int = int(disk_size[:-1])
            except Exception as e:
                print("Disk size must be an integer.")
                continue
            if disk_size_int < 2 or disk_size_int > 128:
                print("Please enter a number between 2 and 128.")
                continue
            else:
                break
        username = input("Enter username: ")
        password = input("Enter password: ")

        vm_config = {
            "vpc_id": f"{vpc_name}",
            "vm_name": vm_name,
            "hostname": hostname,
            "vcpus": vcpus,
            "memory": memory,
            "disk_size": disk_size,
            "username": username,
            "password": password,
        }

        vm_configurations.append(vm_config)

    return vm_configurations

def assign_subnets(existing_subnets, vpc_name, vm_configurations):
    print("Assigning subnets for VPC {}:".format(vpc_name))
    print("1. Want to assign a single subnet to all VMs?")
    print("2. Want to assign individual subnets to each VM?")
    print("3. Want to assign multiple VMs to a single subnet?")

    subnet_option = input("Enter your choice (1/2/3): ")

    if subnet_option == "1":
        subnet = input("Enter the subnet to be assigned to all VMs: ")
        if not check_subnet_overlap(subnet, existing_subnets, f"{vpc_name}"):
            existing_subnets[f"{vpc_name}"] = {subnet}
            start_ip, end_ip = calculate_subnet_range(subnet)
            for vm_config in vm_configurations:
                vm_config["subnet"] = subnet
                vm_config["start_ip"] = start_ip
                vm_config["end_ip"] = end_ip
        else:
            print("Subnet overlaps with existing subnets. Please enter a different subnet.")

    elif subnet_option == "2":
        for vm_config in vm_configurations:
          while True:
            subnet = input(f"Enter the subnet for VM {vm_config['hostname']}: ")
            if not check_subnet_overlap(subnet, existing_subnets, f"{vpc_name}"):
                existing_subnets[f"{vpc_name}"] = existing_subnets.get(f"{vpc_name}", set())
                existing_subnets[f"{vpc_name}"].add(subnet)
                start_ip, end_ip = calculate_subnet_range(subnet)
                vm_config["subnet"] = subnet
                vm_config["start_ip"] = start_ip
                vm_config["end_ip"] = end_ip
                break
            else:
                print("Subnet overlaps with existing subnets. Please enter a different subnet.")

    elif subnet_option == "3":
        print("Available VMs:")
        for i, vm_config in enumerate(vm_configurations, 1):
            print(f"{i}. {vm_config['hostname']} - {vm_config['vm_name']}")
        
        chosen_vm_indices = input("Enter the VM numbers to assign to this subnet (separated by commas): ")
        chosen_vm_indices = [int(index) for index in chosen_vm_indices.split(",")]

        subnet = input("Enter the subnet to be assigned to selected VMs: ")
        if not check_subnet_overlap(subnet, existing_subnets, f"{vpc_name}"):
            existing_subnets[f"{vpc_name}"] = {subnet}
            start_ip, end_ip = calculate_subnet_range(subnet)
            for index in chosen_vm_indices:
                vm_configurations[index - 1]["subnet"] = subnet
                vm_configurations[index - 1]["start_ip"] = start_ip
                vm_configurations[index - 1]["end_ip"] = end_ip
        else:
            print("Subnet overlaps with existing subnets. Please enter a different subnet.")

    else:
        print("Invalid choice. Please enter 1, 2, or 3.")

    return existing_subnets

def save_to_yaml(data, filename):
    with open(filename, "a") as yaml_file:
        yaml.dump(data, yaml_file, default_flow_style=False)
        yaml_file.write("\n")

if __name__ == "__main__":
    with open("vpc_database.yaml") as file:
        data = yaml.safe_load(file)

    while True:
        all_vm_configs = []
        existing_subnets = {}  # To store existing subnets for each VPC ID

        input_tenant = input("Enter the tenant name or enter q for quitting: ")
        if input_tenant.lower() == 'q':
            break
        for tenant, vpc_config in data.items():
            if tenant == input_tenant:
                for vpc_name, num_vms in vpc_config.items():
                    vm_configs = get_user_input(tenant, vpc_name, num_vms, existing_subnets)
                    existing_subnets = assign_subnets(existing_subnets, vpc_name, vm_configs)
                    all_vm_configs.extend(vm_configs)

        save_to_yaml(all_vm_configs, "all_vm_configs.yaml")

    print("All VM configurations saved to all_vm_configs.yaml")

