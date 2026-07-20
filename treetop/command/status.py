from tabulate import tabulate
from ..aws_client import get_ec2_client
from ..config import get_instances
from typing import Optional


def status(name: Optional[str]):
    ec2_client = get_ec2_client()

    active_instances = get_instances()

    # Separate instances with and without EC2 IDs
    external_instances = {}
    ec2_instances = {}
    for inst_name, info in active_instances.items():
        if name and inst_name != name:
            continue
        if info.get("id"):
            ec2_instances[inst_name] = info
        else:
            external_instances[inst_name] = info

    if name and not ec2_instances and not external_instances:
        print(f"No active instance found with name: {name}")
        return

    if not ec2_instances and not external_instances:
        print("No active instances found.")
        return

    table_data = []

    # Query EC2 for instances that have IDs
    if ec2_instances:
        instance_ids = [info["id"] for info in ec2_instances.values()]
        instances = []
        reservations = ec2_client.describe_instances(InstanceIds=instance_ids)['Reservations']
        for reservation in reservations:
            for instance in reservation['Instances']:
                instances.append(instance)

        for instance in instances:
            inst_id = instance['InstanceId']
            inst_name = next(n for n, info in ec2_instances.items() if info["id"] == inst_id)
            instance_state = instance['State']['Name']
            table_data.append([inst_name, inst_id, instance_state])

    # Add external instances (no EC2 ID)
    for inst_name, info in external_instances.items():
        ip = info.get("ip_address", "N/A")
        table_data.append([inst_name, f"external ({ip})", "unknown"])

    headers = ["Instance Name", "Instance ID", "Instance Type", "State"]
    print(tabulate(table_data, headers, tablefmt="grid"))


def add_command(subparser):
    def _status(args):
        status(args.name)

    parser = subparser.add_parser(
        "status",
        help="Print status of all active instances, or a single instance if specified",
    )
    parser.set_defaults(func=_status)
    parser.add_argument("name", help="The name of the instance to check", nargs="?")
