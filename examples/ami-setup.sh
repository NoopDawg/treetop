#!/bin/bash
# Reference script for building a base AMI for use with Treetop.
#
# Typical workflow:
# 1. Launch a base Ubuntu/Amazon Linux instance
# 2. SSH in and run this script (or your customized version)
# 3. Create an AMI from the instance via AWS Console or CLI:
#    aws ec2 create-image --instance-id i-xxx --name "treetop-base-$(date +%Y%m%d)"
# 4. Use the resulting AMI ID in `treetop init` or `treetop create-template`

set -e

# Update system packages
sudo apt-get update && sudo apt-get upgrade -y

# Install common development tools
sudo apt-get install -y \
    git \
    curl \
    wget \
    build-essential \
    python3 \
    python3-pip \
    python3-venv

# Optional: Install Docker
# sudo apt-get install -y docker.io
# sudo usermod -aG docker ubuntu

# Optional: Install AWS CLI v2
# curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
# unzip awscliv2.zip && sudo ./aws/install && rm -rf aws awscliv2.zip

# Optional: Install EFS utilities (needed if you mount EFS in your launch template)
# sudo apt-get install -y amazon-efs-utils

echo "Base AMI setup complete. Create an image from this instance."
