def make_box_row(text, box_width, pad=4):
    padding = " " * pad
    return f"#{padding}{text.ljust(box_width - len(padding) - 2)}#"

def report_instance_launch(instance_id, instance_name, key_location, ip_address):
    box_width = 60
    padding = " " * 4
    top_bottom_padding = "#" + " " * (box_width - 2) + "#"
    border_line = "#" * box_width

    instance_info = f"""{make_box_row("Instance Active", box_width)}
{make_box_row(f"Instance Name: {instance_name}", box_width)}
{make_box_row(f"Instance ID: {instance_id}", box_width)}"""

    ssh_command = f"""
To connect to this instance use the command:

ssh -i {key_location} ubuntu@{ip_address}
"""

    print(f"""
{border_line}
{top_bottom_padding}
{instance_info}
{top_bottom_padding}
{border_line}
{ssh_command}
""")