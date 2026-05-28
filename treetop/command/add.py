from ..aws_client import get_ec2_client
from ..config import record_external_instance
from ..prompt_utils import input_with_path_completion


def lookup_instance_id_by_ip(ip_address):
    ec2_client = get_ec2_client()
    response = ec2_client.describe_instances(
        Filters=[{"Name": "private-ip-address", "Values": [ip_address]}]
    )
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            return instance["InstanceId"]
    return None


def add():
    name = input("Enter a name for this instance: ")
    ip_address = input("Enter the IP address: ")
    username = input("Enter the SSH username [ubuntu]: ").strip() or "ubuntu"
    pem_key_location = input_with_path_completion("Enter the path to the PEM key: ").strip()

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
