import os
import json
from typing import Optional


CONFIG_DIR = os.path.join(os.environ["HOME"], ".treetop")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
ACTIVE_INSTANCES_FILE = os.path.join(CONFIG_DIR, "active_instances.json")


class ConfigNotFoundError(Exception):
    pass


def load_config() -> dict:
    if not os.path.exists(CONFIG_FILE):
        raise ConfigNotFoundError(
            "Configuration file not found. Run 'treetop init' to set up your environment."
        )
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def save_config(config: dict):
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)


def get_aws_region() -> str:
    config = load_config()
    aws = config.get("aws", {})
    region = aws.get("region")
    if not region:
        raise ConfigNotFoundError(
            "AWS region not configured. Run 'treetop init' to set up your environment."
        )
    return region


def get_launch_template_id() -> Optional[str]:
    config = load_config()
    return config.get("aws", {}).get("launch_template_id")


def get_default_instance_type() -> str:
    config = load_config()
    return config.get("aws", {}).get("default_instance_type", "t2.medium")


def get_template_defaults() -> dict:
    config = load_config()
    return config.get("template_defaults", {})


def get_ssh_key_name() -> str:
    config = load_config()
    key_name = config.get("ssh_key_name")
    if not key_name:
        raise ConfigNotFoundError(
            "SSH key name not configured. Run 'treetop init' to set up your environment."
        )
    return key_name


def get_ssh_key_location() -> str:
    config = load_config()
    key_location = config.get("ssh_key_location")
    if not key_location:
        raise ConfigNotFoundError(
            "SSH key location not configured. Run 'treetop init' to set up your environment."
        )
    return key_location


def update_ssh_config(name, ip_address, identity_file, remove=False, username="ubuntu"):
    ssh_config_path = os.path.expanduser("~/.ssh/config")
    if not os.path.exists(os.path.dirname(ssh_config_path)):
        os.makedirs(os.path.dirname(ssh_config_path))

    if not os.path.exists(ssh_config_path):
        open(ssh_config_path, "w").close()

    with open(ssh_config_path, "r") as f:
        lines = f.readlines()

    updated_lines = []
    skip = False

    for line in lines:
        if line.strip() == f"Host {name}":
            skip = True
        elif skip and line.startswith("Host "):
            skip = False

        if not skip:
            updated_lines.append(line)

    if not remove:
        updated_lines.append(f"\nHost {name}\n")
        updated_lines.append(f"  HostName {ip_address}\n")
        updated_lines.append(f"  IdentityFile {identity_file}\n")
        updated_lines.append(f"  User {username}\n")

    with open(ssh_config_path, "w") as f:
        f.writelines(updated_lines)


def record_active_instance(name, instance_id, ip_address):
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

    if os.path.exists(ACTIVE_INSTANCES_FILE):
        with open(ACTIVE_INSTANCES_FILE, "r") as f:
            active_instances = json.load(f)
    else:
        active_instances = {}

    if name in active_instances:
        raise ValueError(f"An instance with the name '{name}' already exists. Please choose a different name.")

    active_instances[name] = {"name": name, "id": instance_id}

    with open(ACTIVE_INSTANCES_FILE, "w") as f:
        json.dump(active_instances, f, indent=4)

    identity_file = get_ssh_key_location()
    update_ssh_config(name, ip_address, identity_file)


def record_external_instance(name, instance_id, ip_address, username, pem_key_location):
<<<<<<< HEAD
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

    if os.path.exists(ACTIVE_INSTANCES_FILE):
        with open(ACTIVE_INSTANCES_FILE, "r") as f:
=======
    config_dir = os.path.join(os.environ["HOME"], ".treetop")
    active_instances_file = os.path.join(config_dir, "active_instances.json")

    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    if os.path.exists(active_instances_file):
        with open(active_instances_file, "r") as f:
>>>>>>> c04b7bd (adding add command to register external instances)
            active_instances = json.load(f)
    else:
        active_instances = {}

    if name in active_instances:
        raise ValueError(f"An instance with the name '{name}' already exists. Please choose a different name.")

    entry = {"name": name, "ip_address": ip_address, "username": username, "pem_key_location": pem_key_location}
    if instance_id:
        entry["id"] = instance_id

    active_instances[name] = entry

<<<<<<< HEAD
    with open(ACTIVE_INSTANCES_FILE, "w") as f:
=======
    with open(active_instances_file, "w") as f:
>>>>>>> c04b7bd (adding add command to register external instances)
        json.dump(active_instances, f, indent=4)

    update_ssh_config(name, ip_address, pem_key_location, username=username)


def delete_instance_config(name):
    with open(ACTIVE_INSTANCES_FILE, "r") as f:
        active_instances = json.load(f)

    if name in active_instances:
        del active_instances[name]

    with open(ACTIVE_INSTANCES_FILE, "w") as f:
        json.dump(active_instances, f, indent=4)

    update_ssh_config(name, None, None, remove=True)


def get_instances() -> dict:
    if not os.path.exists(ACTIVE_INSTANCES_FILE):
        return {}

    with open(ACTIVE_INSTANCES_FILE, "r") as f:
        return json.load(f)


def get_last_connected_instance() -> Optional[str]:
    try:
        config = load_config()
    except ConfigNotFoundError:
        return None
    return config.get("last_connected_instance")


def set_last_connected_instance(name):
    config = load_config()
    config["last_connected_instance"] = name
    save_config(config)
