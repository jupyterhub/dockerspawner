def default_format_volume_name(template, spawner):
    return template.format(username=spawner.user.name)

def escaped_format_volume_name(label_template, spawner):
    return label_template.format(username=spawner.escaped_name)

