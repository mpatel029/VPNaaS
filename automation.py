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
            config['veth_subnet'] = vpc_subnets[vpc_id]
        else:
            # Generate subnet for veth_subnet and update dictionary
            veth_subnet = generate_subnet('100.64.0.0/30', len(vpc_subnets))
            config['veth_subnet'] = str(veth_subnet)
            vpc_subnets[vpc_id] = str(veth_subnet)
    
    vpc_id = config['vpc_id']
    vm_name = config['vm_name']
    # Extract first three letters of VPC name and VM name
    vpc_prefix = vpc_id[:3]
    vm_prefix = vm_name[:3]
    # Generate key name
    key = f"{vpc_id}_{vm_name}"
    # Generate formatted values
    br_value = f"{vpc_prefix}{vm_prefix}_br"
    ns_value = f"{vpc_prefix}{vm_prefix}_ns"
    # Update the original parsed YAML with the new values
    config['veth_bridge'] = br_value
    config['veth_namespace'] = ns_value

# Write the updated parsed YAML content back to the same file
with open('all_vm_configs.yaml', 'w') as file:
    yaml.dump(parsed_yaml, file)

print("YAML file has been updated successfully!")
