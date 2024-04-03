import subprocess

# Run scripts for user inputs
subprocess.run(["python3", "tenant.py"])
subprocess.run(["python3", "vpc_data.py"])
subprocess.run(["python3", "subnet.py"])
subprocess.run(["python3", "automation.py"])

# Run ansible playbook for vm-creation
subprocess.run(["ansible-playbook", "vm_creations.yaml"])

# Run bridge_creation script to connect bridges to new vms
subprocess.run(["python3", "bridge_creation.py"])

# Run ansible playbook to create NS for each VPC
subprocess.run(["ansible-playbook", "namespace_creation.yaml"])
