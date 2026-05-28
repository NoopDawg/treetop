# IAM Permissions for Treetop

Treetop requires the following EC2 permissions to function. You can attach this policy to the IAM user or role that will run the CLI.

## Minimum Required Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:RunInstances",
        "ec2:StartInstances",
        "ec2:StopInstances",
        "ec2:TerminateInstances",
        "ec2:DescribeInstances",
        "ec2:DescribeRegions",
        "ec2:CreateTags"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ec2:CreateLaunchTemplate"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "sts:GetCallerIdentity"
      ],
      "Resource": "*"
    }
  ]
}
```

## Scoping to Treetop Resources

For tighter security, you can restrict instance actions to only instances tagged with `Project=Treetop`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:StartInstances",
        "ec2:StopInstances",
        "ec2:TerminateInstances"
      ],
      "Resource": "arn:aws:ec2:*:*:instance/*",
      "Condition": {
        "StringEquals": {
          "aws:ResourceTag/Project": "Treetop"
        }
      }
    },
    {
      "Effect": "Allow",
      "Action": [
        "ec2:RunInstances",
        "ec2:DescribeInstances",
        "ec2:DescribeRegions",
        "ec2:CreateTags",
        "ec2:CreateLaunchTemplate"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": "sts:GetCallerIdentity",
      "Resource": "*"
    }
  ]
}
```

## Notes

- `ec2:RunInstances` requires access to multiple resource types (instances, volumes, network interfaces, launch templates). Scoping it narrowly requires additional ARN conditions.
- The `sts:GetCallerIdentity` permission is used by `treetop init` to validate credentials.
- If you use the `add` command to look up instances by IP, `ec2:DescribeInstances` must not be restricted to tagged resources.
