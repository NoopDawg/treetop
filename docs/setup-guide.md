# Setup Guide

This guide walks you through setting up Treetop in a fresh AWS environment.

## Prerequisites

- An AWS account with programmatic access configured (`aws configure` or environment variables)
- Python 3.9+
- SSH key pair

## Step 1: Network Infrastructure

You need a VPC with at least one subnet where instances will launch. Most AWS accounts already have a default VPC. If you need a custom setup:

1. Create a VPC (or use the default)
2. Create a subnet (or use an existing one) — note the subnet ID
3. Create a security group that allows SSH (port 22) inbound from your network — note the security group ID

## Step 2: SSH Key Pair

Create or import an SSH key pair in EC2:

```bash
# Create a new key pair
aws ec2 create-key-pair --key-name treetop-key --query 'KeyMaterial' --output text > ~/.ssh/treetop-key.pem
chmod 400 ~/.ssh/treetop-key.pem

# Or import an existing public key
aws ec2 import-key-pair --key-name treetop-key --public-key-material fileb://~/.ssh/id_rsa.pub
```

## Step 3: AMI (Amazon Machine Image)

You need an AMI that your instances will boot from. Options:

- **Use a stock Ubuntu AMI** — find the latest at https://cloud-images.ubuntu.com/locator/ec2/
- **Build a custom AMI** — see `examples/ami-setup.sh` for a reference script

Note the AMI ID (e.g., `ami-0abcdef1234567890`).

## Step 4: (Optional) EFS Filesystem

If you want shared persistent storage across instances:

```bash
aws efs create-file-system --creation-token treetop-efs --tags Key=Name,Value=treetop-efs
```

Note the filesystem ID. Ensure your security group allows NFS (port 2049) traffic.

## Step 5: Install Treetop

```bash
pip install treetop
```

Or from source:

```bash
git clone <repository-url>
cd treetop
pip install -e .
```

## Step 6: Configure

```bash
treetop init
```

This interactive command will:
1. Verify your AWS credentials
2. Ask for your region, SSH key, and instance preferences
3. Optionally create a launch template with your AMI, subnet, and security group

## Step 7: Launch Your First Instance

```bash
treetop launch my-dev-box
```

## Step 8: Connect

```bash
treetop connect my-dev-box
```

## IAM Permissions

See [iam-permissions.md](iam-permissions.md) for the minimum IAM policy required.
