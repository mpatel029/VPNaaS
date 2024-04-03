# PT07 VPNaaS

## Northbound steps in order:

1. Run `tenant.py` and fill in tenant information.
2. Run `vpc_data.py` and fill in VPC and VM count for the tenant.
3. Run `subnet.py` to configure individual VMs and subnets and save to the configuration file `all_vm_configs.yaml`.

### Southbound steps in order:

1. Run `ansible-playbook vm_creation.yaml` to provision VMs according to the configuration file.
2. Run `automation.py` to parse and format the file with subnet, bridge, and namespace names.
3. Run `bridge_creation.py` to create, configure, and attach bridges to VMs.
4. Run `ansible-playbook namespace_creation.yaml` to create and configure namespaces and veth pairs and start dnsmasq for DHCP.
