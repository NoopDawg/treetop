#!/bin/bash
# Example user-data script for a Treetop launch template.
# This runs on first boot of an EC2 instance.

set -e

# Optional: Mount an EFS filesystem
# Replace fs-XXXXXXXXX with your EFS ID
# EFS_ID="fs-XXXXXXXXX"
# yum install -y amazon-efs-utils || apt-get install -y amazon-efs-utils
# mkdir -p /mnt/efs
# echo "${EFS_ID}:/ /mnt/efs efs defaults,_netdev 0 0" >> /etc/fstab
# mount -a

# Optional: Install development tools
# apt-get update && apt-get install -y git python3-pip docker.io

echo "Instance setup complete"
