import time
from ..aws_client import get_ec2_client
from ..config import get_ssh_key_location, record_active_instance, get_instances, update_ssh_config
from ..utils import report_instance_launch


def start_instance(instance_id, name):
    ec2_client = get_ec2_client()
    ec2_client.start_instances(InstanceIds=[instance_id])
    waiter = ec2_client.get_waiter('instance_running')
    waiter.wait(InstanceIds=[instance_id], WaiterConfig={'Delay': 15, 'MaxAttempts': 40})

    instance = ec2_client.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]
    private_ip = instance.get('PrivateIpAddress')
    report_instance_launch(instance_id, name, get_ssh_key_location(), private_ip)


def up(name: str):
    ec2_client = get_ec2_client()
    active_instances = get_instances()
    instance_info = active_instances.get(name)

    if instance_info:
        instance_id = instance_info.get("id")
        if not instance_id:
            print(f"Instance {name} has no EC2 instance ID. Cannot start it via treetop.")
            return
        instance = ec2_client.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]
        status = instance['State']['Name']

        ip_address = instance.get('PrivateIpAddress')
        identity_file = get_ssh_key_location()

        if status == "running":
            print(f"Instance {name} is already running.")
            report_instance_launch(instance_id, name, identity_file, instance.get('PrivateIpAddress'))
        else:
            print(f"Starting instance {name}...")
            start_instance(instance_id, name)
            update_ssh_config(name, ip_address, identity_file)
    else:
        print(f"No instance found with name: {name}")


def add_command(subparser):
    def _up(args):
        up(args.name)

    parser = subparser.add_parser(
        "up",
        help="Start an existing instance or notify if it is already running.",
    )
    parser.set_defaults(func=_up)
    parser.add_argument(
        "name",
        help="The name of the instance to start",
    )
