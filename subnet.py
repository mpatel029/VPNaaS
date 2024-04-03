import yaml
import ipaddress

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

def get_user_input(tenant, vpc_num, num_vms, existing_subnets):
    vm_configurations = []
    print("Configuring for {} VPC {}".format(tenant, vpc_num))

    for i in range(1, num_vms + 1):
        print(f"Configuring VM {i}")
        vm_name = input(f"Enter the name for VM {i}: ")
        vcpus = 0
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
        memory = 0
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
        disk_size = ""
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

        while True:
            subnet = input("Enter subnet: ")
            if not check_subnet_overlap(subnet, existing_subnets, f"{tenant}{vpc_num}"):
                if f"{tenant}{vpc_num}" not in existing_subnets:
                    existing_subnets[f"{tenant}{vpc_num}"] = set()
                existing_subnets[f"{tenant}{vpc_num}"].add(subnet)
                break
            else:
                print("Subnet overlaps with existing subnets. Please enter a different subnet.")
        start_ip, end_ip = calculate_subnet_range(subnet)
        bridge_name = f"{tenant}{vpc_num}_{vm_name}"
        vm_config = {
            "vpc_id": f"{tenant}{vpc_num}",
            "vm_name": vm_name,
            "vcpus": int(vcpus),
            "memory": int(memory),
            "disk_size": disk_size,
            "username": username,
            "password": password,
            "subnet": subnet,
            "start_ip": start_ip,
            "end_ip": end_ip,
            "bridge":bridge_name
        }

        vm_configurations.append(vm_config)

    return vm_configurations

def save_to_yaml(data, filename):
    with open(filename, "a") as yaml_file:
        yaml_file.write("vm_configurations:\n")  # Add "vm_configurations:" at the top
        for vm_config in data:
            yaml.dump(vm_config, yaml_file, default_flow_style=False)
            yaml_file.write("\n")

if __name__ == "__main__":
    with open("vpc_database.json") as file:
        data = yaml.safe_load(file)

    while True:
        all_vm_configs = []
        existing_subnets = {}  # To store existing subnets for each VPC ID

        input_tenant = input("Enter the tenant name or enter q for quitting: ")
        if input_tenant.lower() == 'q':
            break
        for tenant, vpc_config in data.items():
            if tenant == input_tenant:
                for vpc_num, num_vms in vpc_config.items():
                    vm_configs = get_user_input(tenant, vpc_num, num_vms, existing_subnets)
                    all_vm_configs.extend(vm_configs)

        save_to_yaml(all_vm_configs, "all_vm_configs.yaml")

    print("All VM configurations saved to all_vm_configs.yaml")

