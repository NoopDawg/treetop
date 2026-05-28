import time
from ..aws_client import get_ec2_client
from ..config import delete_instance_config, get_instances


def wait_for_instance_termination(instance_id, timeout):
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

            if status == "terminated":
                break

            if time.time() > deadline:
                raise TimeoutError()

            time.sleep(2)
    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Instance will terminate in the background.\n")
        print("Use `treetop status` to show the state of the instance.\n")


def delete(name: str = None, instance_id: str = None):
    ec2_client = get_ec2_client()
    active_instances = get_instances()

    if instance_id:
        instance = ec2_client.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]
        instance_name = next(tag['Value'] for tag in instance['Tags'] if tag['Key'] == 'Name')
    elif name:
        instance_info = active_instances.get(name)
        if not instance_info:
            print(f"No active instance found with name: {name}")
            return
        instance_id = instance_info["id"]
        instance_name = name
    else:
        raise ValueError("Either instance name or instance ID must be provided.")

    instance = ec2_client.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]
    status = instance['State']['Name']
    print(f"Requesting termination of {instance_name}...")

    if status == "terminated":
        delete_instance_config(instance_name)
        print(f"Instance {instance_name} is already terminated.")
        return

    ec2_client.terminate_instances(InstanceIds=[instance_id])
    delete_instance_config(instance_name)
    wait_for_instance_termination(instance_id, 5 * 60)
    print(f"Instance {instance_name} terminated.")


def add_command(subparser):
    def _delete(args):
        delete(args.name, args.instance_id)

    parser = subparser.add_parser(
        "delete",
        help="Terminate the instance and delete the persistent disk associated with the specified instance config",
    )
    parser.set_defaults(func=_delete)
    parser.add_argument(
        "name",
        help="The name of the instance config to delete the volume for",
        nargs="?",
        default=None,
    )
    parser.add_argument(
        "--instance-id",
        help="The ID of the instance to terminate (optional)",
        default=None,
    )
