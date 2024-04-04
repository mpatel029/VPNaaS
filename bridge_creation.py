import yaml
import subprocess

def create_bridge(bridge_name):
    # Check if the bridge already exists
    existing_bridges = subprocess.run(["brctl", "show"], capture_output=True, text=True, check=True).stdout
    if bridge_name in existing_bridges:
        print(f"Bridge {bridge_name} already exists. Skipping creation.")
    else:
        subprocess.run(["sudo", "brctl", "addbr", bridge_name], check=True)

def attach_interface(vm_name, bridge_name):
    subprocess.run(["sudo", "virsh", "attach-interface", "--domain", vm_name, "--type", "bridge", "--source", bridge_name, "--model", "virtio"], check=True)
    subprocess.run(["sudo", "brctl", "stp", bridge_name, "yes"], check=True)
    subprocess.run(["sudo", "ip", "link", "set", bridge_name, "up"], check=True)
def main():
    with open("all_vm_configs.yaml", "r") as file:
        data = yaml.safe_load(file)

    for config in data.get("vm_configurations", []):
        vm_name = config.get("vm_name")
        vpc_id = config.get("vpc_id")
        bridge_name = f"{vpc_id}_{vm_name}"
        create_bridge(bridge_name)
        attach_interface(vm_name, bridge_name)

if __name__ == "__main__":
    main()

