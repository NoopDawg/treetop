from ..aws_client import get_ec2_client
from ..config import (
    get_ssh_key_location,
    get_ssh_key_name,
    get_launch_template_id,
    get_default_instance_type,
    record_active_instance,
)
from ..utils import report_instance_launch

INSTANCE_TYPES = [
    "t2.small",
    "t2.medium",
    "t2.large",
    "t2.xlarge",
    "t2.2xlarge",
    "t3.small",
    "t3.medium",
    "t3.large",
    "t3.xlarge",
    "t3.2xlarge",
    "g5.xlarge",
    "g5.2xlarge",
    "g5.4xlarge",
]


def start_instance_from_template(launch_template_id, instance_type=None, name="Treetop-Workspace"):
    ec2_client = get_ec2_client()

    key_name = get_ssh_key_name()
    key_location = get_ssh_key_location()

    launch_template_specification = {
        "LaunchTemplateId": launch_template_id,
    }

    response = ec2_client.run_instances(
        InstanceType=instance_type,
        LaunchTemplate=launch_template_specification,
        MinCount=1,
        MaxCount=1,
        KeyName=key_name,
        TagSpecifications=[
            {
                "ResourceType": "instance",
                "Tags": [
                    {"Key": "Name", "Value": name},
                    {"Key": "Project", "Value": "Treetop"},
                ],
            }
        ],
    )

    instance_id = response['Instances'][0]['InstanceId']

    print(f"Starting instance '{name}' with ID: {instance_id}")
    waiter = ec2_client.get_waiter('instance_running')
    waiter.wait(InstanceIds=[instance_id])

    instance = ec2_client.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]
    private_ip = instance.get('PrivateIpAddress')

    record_active_instance(name, instance_id, private_ip)
    report_instance_launch(instance_id, name, key_location, private_ip)

    return instance_id


def launch(name: str, verbose: bool, launch_template_id: str = None, instance_type: str = None):
    if not launch_template_id:
        launch_template_id = get_launch_template_id()
    if not launch_template_id:
        print("No launch template configured. Run 'treetop init' or pass --launch-template-id.")
        return

    if not instance_type:
        instance_type = get_default_instance_type()

    start_instance_from_template(launch_template_id, instance_type, name)


def add_command(subparser):
    def _launch(args):
        launch(args.name, args.verbose, args.launch_template_id, args.instance_type)

    parser = subparser.add_parser(
        "launch", help="Start a compute instance based on a launch template"
    )
    parser.set_defaults(func=_launch)
    parser.add_argument(
        "name",
        help="The name to use when creating instance",
    )
    parser.add_argument(
        "--launch-template-id",
        help="The ID of the launch template to use (reads from config if not specified)",
        default=None,
    )
    parser.add_argument(
        "--instance-type",
        help=f"The instance type to use. Options: {', '.join(INSTANCE_TYPES)}",
        choices=INSTANCE_TYPES,
        default=None,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="If set, will print more logging information showing the server coming online",
    )
