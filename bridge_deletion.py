import yaml
import subprocess

def delete_bridge(bridge_name):
   subprocess.run(["sudo", "ip", "link", "set",bridge_name, "down"], check=True)
   subprocess.run(["sudo", "brctl", "delbr", bridge_name], check=True)

def main():
    with open("all_vm_configs.yaml", "r") as file:
        data = yaml.safe_load(file)

    for config in data.get("vm_configurations", []):
        vm_name = config.get("vm_name")
        vpc_id = config.get("vpc_id")
        bridge_name = f"{vpc_id}_{vm_name}"
        delete_bridge(bridge_name)
        delete_bridge(config.get("veth_namespace"))

if __name__ == "__main__":
    main()
