import sys
from ..config import load_config, save_config, get_template_defaults, CONFIG_DIR, CONFIG_FILE
from ..prompt_utils import input_with_path_completion
from .create_template import create_template
import os


def validate_aws_credentials():
    import boto3
    try:
        sts = boto3.client("sts")
        identity = sts.get_caller_identity()
        print(f"Authenticated as: {identity['Arn']}")
        return True
    except Exception as e:
        print(f"Error: Could not authenticate with AWS. Check your credentials.\n{e}")
        return False


def init():
    print("=== Treetop Configuration ===\n")

    if not validate_aws_credentials():
        sys.exit(1)

    # Load existing config if present (to preserve fields like last_connected_instance)
    existing_config = {}
    try:
        existing_config = load_config()
    except Exception:
        pass

    # AWS region
    current_region = existing_config.get("aws", {}).get("region", "")
    default_region = current_region or "us-east-1"
    region = input(f"AWS region [{default_region}]: ").strip() or default_region

    # SSH key
    current_key_name = existing_config.get("ssh_key_name", "")
    key_name_prompt = f"SSH key pair name (as registered in EC2) [{current_key_name}]: " if current_key_name else "SSH key pair name (as registered in EC2): "
    ssh_key_name = input(key_name_prompt).strip() or current_key_name
    if not ssh_key_name:
        print("Error: SSH key name is required.")
        sys.exit(1)

    current_key_location = existing_config.get("ssh_key_location", "")
    key_loc_prompt = f"Path to SSH private key [{current_key_location}]: " if current_key_location else "Path to SSH private key (e.g. ~/.ssh/my-key.pem): "
    ssh_key_location = input_with_path_completion(key_loc_prompt).strip() or current_key_location
    if not ssh_key_location:
        print("Error: SSH key location is required.")
        sys.exit(1)

    # Default instance type
    current_instance_type = existing_config.get("aws", {}).get("default_instance_type", "t2.medium")
    instance_type = input(f"Default instance type [{current_instance_type}]: ").strip() or current_instance_type

    # Launch template
    current_template_id = existing_config.get("aws", {}).get("launch_template_id", "")
    has_template = input("Do you have an existing launch template? [y/N]: ").strip().lower()

    launch_template_id = None
    template_defaults = existing_config.get("template_defaults", {})

    if has_template in ("y", "yes"):
        template_prompt = f"Launch template ID [{current_template_id}]: " if current_template_id else "Launch template ID: "
        launch_template_id = input(template_prompt).strip() or current_template_id
    else:
        print("\n--- Create a new launch template ---")
        template_name = input("Launch template name: ").strip()
        if not template_name:
            print("Error: Template name is required.")
            sys.exit(1)

        ami_id = input("AMI ID: ").strip()
        if not ami_id:
            print("Error: AMI ID is required.")
            sys.exit(1)

        sg_input = input("Security group IDs (space-separated): ").strip()
        if not sg_input:
            print("Error: At least one security group is required.")
            sys.exit(1)
        security_group_ids = sg_input.split()

        subnet_id = input("Subnet ID: ").strip()
        if not subnet_id:
            print("Error: Subnet ID is required.")
            sys.exit(1)

        efs_id = input("EFS filesystem ID (optional, press Enter to skip): ").strip() or None
        volume_size_str = input("Root volume size in GB [30]: ").strip()
        volume_size = int(volume_size_str) if volume_size_str else 30

        print(f"\nCreating launch template '{template_name}'...")
        try:
            import boto3
            # Temporarily create client with the chosen region
            os.environ.setdefault("AWS_DEFAULT_REGION", region)
            launch_template_id = create_template(
                template_name, instance_type, ami_id, security_group_ids, subnet_id, efs_id, volume_size
            )
        except Exception as e:
            print(f"Error creating launch template: {e}")
            print("You can create a template later with 'treetop create-template'.")
            launch_template_id = None

        template_defaults = {
            "ami_id": ami_id,
            "security_group_ids": security_group_ids,
            "subnet_id": subnet_id,
            "efs_id": efs_id,
            "volume_size": volume_size,
        }

    # Build config
    config = {
        "ssh_key_name": ssh_key_name,
        "ssh_key_location": ssh_key_location,
        "aws": {
            "region": region,
            "default_instance_type": instance_type,
        },
        "template_defaults": template_defaults,
    }

    if launch_template_id:
        config["aws"]["launch_template_id"] = launch_template_id

    # Preserve last_connected_instance if it existed
    if "last_connected_instance" in existing_config:
        config["last_connected_instance"] = existing_config["last_connected_instance"]

    save_config(config)
    print(f"\nConfiguration saved to {CONFIG_FILE}")
    print("Run 'treetop launch <name>' to start an instance.")


def add_command(subparser):
    def _init(args):
        init()

    parser = subparser.add_parser(
        "init", help="Initialize or update Treetop configuration for your AWS environment"
    )
    parser.set_defaults(func=_init)
