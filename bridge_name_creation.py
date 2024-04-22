import yaml

def extract_bridge_subnet_mapping(vm_configurations):
    bridge_subnet_mapping = {}
    bridge_count = {}

    for vm_config in vm_configurations:
        vpc_id = vm_config.get('vpc_id')
        subnet = vm_config.get('subnet')
        if vpc_id and subnet:
            bridge_count[vpc_id] = bridge_count.get(vpc_id, 0) + 1
            bridge_name = f"{vpc_id}-br{bridge_count[vpc_id]}"
            bridge_subnet_mapping.setdefault(vpc_id, {})[bridge_name] = subnet

    return bridge_subnet_mapping

def update_vm_configurations(vm_configurations, bridge_subnet_mapping):
    for vm_config in vm_configurations:
        vpc_id = vm_config.get('vpc_id')
        subnet = vm_config.get('subnet')
        if vpc_id and subnet:
            for bridge, bridge_subnet in bridge_subnet_mapping.get(vpc_id, {}).items():
                if subnet == bridge_subnet:
                    vm_config['bridge'] = bridge
                    break

def main():
    with open("all_vm_configs.yaml", "r") as file:
        data = yaml.safe_load(file)

    vm_configurations = data.get('vm_configurations', [])
    bridge_subnet_mapping = extract_bridge_subnet_mapping(vm_configurations)

    # Update vm_configurations with bridge names
    update_vm_configurations(vm_configurations, bridge_subnet_mapping)

    # Write the updated data back to the file
    with open("all_vm_configs.yaml", "w") as file:
        yaml.dump(data, file)

if __name__ == "__main__":
    main()
