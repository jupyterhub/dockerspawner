def default_format_volume_name(template, spawner):
    return template.format(username=spawner.user.name)

def escaped_format_volume_name(label_template, spawner):
    """Use this strategy if your usernames include illegal characters
    for volume names and you do not use absolute paths in your volume
    label template.
    """
    return label_template.format(username=spawner.escaped_name)

