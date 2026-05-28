import time
from ..aws_client import get_ec2_client
from ..config import get_instances, update_ssh_config


def wait_for_instance_shutdown(instance_id, timeout):
    ec2_client = get_ec2_client()
    deadline = time.time() + timeout
    last_status = None
    try:
        while True:
            instance = ec2_client.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]
            status = instance['State']['Name']

            if status != last_status:
                print(f"Instance {instance_id} is now {status}...")
                last_status = status

            if status == "stopped":
                break

            if time.time() > deadline:
                raise TimeoutError()

            time.sleep(2)
    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Instance will continue to shutdown in the background.\n")
        print("Use `treetop status` to show the state of the instance.\n")


def down(name: str = None, instance_id: str = None):
    ec2_client = get_ec2_client()

    if instance_id:
        instance = ec2_client.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]
        instance_name = next(tag['Value'] for tag in instance['Tags'] if tag['Key'] == 'Name')
    elif name:
        active_instances = get_instances()
        instance_info = active_instances.get(name)
        if not instance_info:
            print(f"No active instance found with name: {name}")
            return
        instance_id = instance_info.get("id")
        if not instance_id:
            print(f"Instance {name} has no EC2 instance ID. Cannot stop it via treetop.")
            return
        instance_name = name
    else:
        raise ValueError("Either instance name or instance ID must be provided.")

    instance = ec2_client.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]
    status = instance['State']['Name']
    if status == "terminated":
        print(f"Instance {instance_name} appears to be offline already.")
    else:
        if status == "running":
            print(f"Requesting graceful shutdown of {instance_name}...")

            try:
                ec2_client.stop_instances(InstanceIds=[instance_id])
            except Exception as e:
                print(f"Error stopping instance: {e}")

            update_ssh_config(name, None, None, remove=True)
            print("Allow up to 5 minutes for graceful shutdown...")
            try:
                wait_for_instance_shutdown(instance_id, timeout=5 * 60)
            except TimeoutError:
                pass

        print(f"Instance {instance_name} stopped but not terminated.")


def add_command(subparser):
    def _down(args):
        down(args.name, args.instance_id)

    parser = subparser.add_parser(
        "down",
        help="Stop an instance without terminating it.",
    )
    parser.set_defaults(func=_down)
    parser.add_argument(
        "name",
        help="The name of the instance to stop",
        nargs="?",
        default=None,
    )
    parser.add_argument(
        "--instance-id",
        help="The ID of the instance to stop (optional)",
        default=None,
    )
