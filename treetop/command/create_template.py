import base64
from ..aws_client import get_ec2_client
from ..config import get_template_defaults, get_default_instance_type


def create_template(launch_template_name, instance_type, ami_id, security_group_ids, subnet_id, efs_id, volume_size):
    ec2_client = get_ec2_client()

    launch_template_data = {
        "ImageId": ami_id,
        "InstanceType": instance_type,
        "BlockDeviceMappings": [
            {
                "DeviceName": "/dev/xvda",
                "Ebs": {
                    "VolumeSize": volume_size,
                    "VolumeType": "gp3",
                    "DeleteOnTermination": True,
                },
            }
        ],
        "TagSpecifications": [
            {
                "ResourceType": "instance",
                "Tags": [
                    {"Key": "Name", "Value": "Treetop-Workspace"},
                    {"Key": "Project", "Value": "Treetop"},
                ],
            }
        ],
        "NetworkInterfaces": [
            {
                "SubnetId": subnet_id,
                "DeviceIndex": 0,
                "AssociatePublicIpAddress": False,
                "Groups": security_group_ids,
            }
        ],
    }

    if efs_id:
        user_data_script = f"""#!/bin/bash
yum install -y amazon-efs-utils || apt-get install -y amazon-efs-utils
mkdir -p /mnt/efs
echo "{efs_id}:/ /mnt/efs efs defaults,_netdev 0 0" >> /etc/fstab
mount -a
"""
        launch_template_data["UserData"] = base64.b64encode(
            user_data_script.encode("utf-8")
        ).decode("utf-8")

    response = ec2_client.create_launch_template(
        LaunchTemplateName=launch_template_name,
        LaunchTemplateData=launch_template_data,
    )

    template_id = response['LaunchTemplate']['LaunchTemplateId']
    print(f"Launch Template Created: {template_id}")
    return template_id


def add_command(subparser):
    defaults = {}
    try:
        defaults = get_template_defaults()
    except Exception:
        pass

    def _create_template(args):
        if not args.ami_id:
            print("Error: --ami-id is required. Specify an AMI ID or configure it via 'treetop init'.")
            return
        if not args.security_group_ids:
            print("Error: --security-group-ids is required.")
            return
        if not args.subnet_id:
            print("Error: --subnet-id is required.")
            return

        create_template(
            args.launch_template_name,
            args.instance_type,
            args.ami_id,
            args.security_group_ids,
            args.subnet_id,
            args.efs_id,
            args.volume_size
        )

    parser = subparser.add_parser(
        "create-template", help="Create a new EC2 launch template"
    )
    parser.set_defaults(func=_create_template)
    parser.add_argument(
        "launch_template_name",
        help="The name of the launch template to create",
    )
    parser.add_argument(
        "--instance-type",
        default=defaults.get("instance_type", "t2.medium"),
        help="The instance type to use (default: t2.medium)",
    )
    parser.add_argument(
        "--ami-id",
        default=defaults.get("ami_id"),
        help="The AMI ID to use",
    )
    parser.add_argument(
        "--security-group-ids",
        default=defaults.get("security_group_ids"),
        nargs='+',
        help="The security group IDs to associate",
    )
    parser.add_argument(
        "--subnet-id",
        default=defaults.get("subnet_id"),
        help="The subnet ID to use",
    )
    parser.add_argument(
        "--efs-id",
        default=defaults.get("efs_id"),
        help="The EFS filesystem ID to mount (optional)",
    )
    parser.add_argument(
        "--volume-size",
        type=int,
        default=defaults.get("volume_size", 30),
        help="The root volume size in GB (default: 30)",
    )
