import ipaddress
import yaml

def generate_subnet(start_ip, offset):
    # Convert the start IP address to an IPv4Network object
    network = ipaddress.IPv4Network(start_ip)

    # Increment the third octet with the offset
    new_ip = network.network_address + (offset * 256)

    # Create a new subnet with the updated IP and a prefix length of /30
    subnet = ipaddress.IPv4Network((new_ip, 30))

    return subnet

# Load YAML content from file
with open('all_vm_configs.yaml', 'r') as file:
    yaml_content = file.read()

# Parse YAML
parsed_yaml = yaml.safe_load(yaml_content)

# Keep track of vpc_id and corresponding veth_subnet
vpc_subnets = {}

# Iterate through each VM configuration
for config in parsed_yaml['vm_configurations']:
    if 'vpc_id' in config:
        vpc_id = config['vpc_id']
        # Check if vpc_id already exists in the dictionary
        if vpc_id in vpc_subnets:
            # If vpc_id exists, use the existing veth_subnet
            config['psubnet'] = vpc_subnets[vpc_id]
        else:
            # Generate subnet for veth_subnet and update dictionary
            veth_provider = generate_subnet('100.10.0.0/30', len(vpc_subnets))
            config['psubnet'] = str(veth_provider)
            vpc_subnets[vpc_id] = str(veth_provider)

    vpc_id = config['vpc_id']
    # Generate key name
    key = f"{vpc_id}"
    # Generate formatted values
    pr_value = f"{vpc_id}_pr"
    vpc_value = f"{vpc_id}_vpc"
    # Update the original parsed YAML with the new values
    config['veth_provider'] = pr_value
    config['veth_vpc'] = vpc_value

# Write the updated parsed YAML content back to the same file
with open('all_vm_configs.yaml', 'w') as file:
    yaml.dump(parsed_yaml, file)

print("YAML file has been updated successfully!")
