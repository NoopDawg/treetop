import subprocess
from typing import Optional
from ..aws_client import get_ec2_client
from ..config import get_instances, get_ssh_key_location, get_last_connected_instance, set_last_connected_instance


def connect(name: Optional[str] = None):
    if not name:
        name = get_last_connected_instance()
        if not name:
            print("No instance name provided and no last connected instance found.")
            print("Usage: treetop connect <name>")
            return

    ec2_client = get_ec2_client()
    active_instances = get_instances()
    instance_info = active_instances.get(name)

    if not instance_info:
        print(f"No instance found with name: {name}")
        return

    # Use per-instance SSH settings if available (external instances)
    ip_address = instance_info.get("ip_address")
    identity_file = instance_info.get("pem_key_location")
    username = instance_info.get("username", "ubuntu")

    instance_id = instance_info.get("id")

    if instance_id:
        instance = ec2_client.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]
        status = instance['State']['Name']

        if status != "running":
            print(f"Instance {name} is not running. Current status: {status}")
            return

        ip_address = instance.get('PrivateIpAddress') or ip_address

    if not ip_address:
        print(f"Instance {name} does not have an IP address assigned.")
        return

    if not identity_file:
        identity_file = get_ssh_key_location()

    set_last_connected_instance(name)

    ssh_command = ['ssh', '-i', identity_file, f'{username}@{ip_address}']
    subprocess.run(ssh_command)


def add_command(subparser):
    def _connect(args):
        connect(args.name)

    parser = subparser.add_parser(
        "connect",
        help="Establish an SSH connection to the specified instance, or the last connected instance if no name is provided.",
    )
    parser.set_defaults(func=_connect)
    parser.add_argument(
        "name",
        nargs="?",
        help="The name of the instance to connect to (optional, uses last connected instance if omitted)",
    )
