import boto3
import readline
import glob
import os
import sys


def _path_completer(text, state):
    """Tab-complete file paths. Expands ~ and appends / to directories."""
    expanded = os.path.expanduser(text)
    matches = glob.glob(expanded + "*")
    matches = [
        (m + os.sep if os.path.isdir(m) else m)
        for m in matches
    ]
    # Re-insert ~ prefix if the user typed it
    if text.startswith("~"):
        home = os.path.expanduser("~")
        matches = [m.replace(home, "~", 1) for m in matches]
    return matches[state] if state < len(matches) else None


def _input_with_path_completion(prompt):
    """input() with filesystem tab completion enabled."""
    old_completer = readline.get_completer()
    old_delims = readline.get_completer_delims()

    # Remove / from delims so paths aren't split at slashes
    readline.set_completer_delims(old_delims.replace("/", "").replace("~", ""))
    readline.set_completer(_path_completer)

    try:
        return input(prompt)
    finally:
        readline.set_completer(old_completer)
        readline.set_completer_delims(old_delims)


def lookup_instance_id_by_ip(ip_address):
    ec2_client = boto3.client("ec2", region_name="us-east-1")
    response = ec2_client.describe_instances(
        Filters=[{"Name": "private-ip-address", "Values": [ip_address]}]
    )
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            return instance["InstanceId"]
    return None


def add():
    from ..config import record_external_instance

    # Enable tab completion (macOS uses libedit, Linux uses GNU readline)
    if "libedit" in readline.__doc__:
        readline.parse_and_bind("bind ^I rl_complete")
    else:
        readline.parse_and_bind("tab: complete")

    name = input("Enter a name for this instance: ")
    ip_address = input("Enter the IP address: ")
    username = input("Enter the SSH username [ubuntu]: ").strip() or "ubuntu"
    pem_key_location = _input_with_path_completion("Enter the path to the PEM key: ").strip()

    print(f"Looking up instance ID for {ip_address}...")
    instance_id = lookup_instance_id_by_ip(ip_address)

    if not instance_id:
        print(f"Warning: Could not find an EC2 instance with IP {ip_address}.")
        print("The instance will be added but 'up' and 'down' commands will not work.")

    record_external_instance(name, instance_id, ip_address, username, pem_key_location)
    print(f"Instance '{name}' added successfully.")


def add_command(subparser):
    def _add(args):
        add()

    parser = subparser.add_parser(
        "add",
        help="Add an existing instance (not created by treetop) to your configuration.",
    )
    parser.set_defaults(func=_add)
