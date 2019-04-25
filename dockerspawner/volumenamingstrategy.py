def default_format_volume_name(template, spawner):
    return template.format(**spawner.template_namespace())

def escaped_format_volume_name(template, spawner):
    """Use this strategy if your usernames include illegal characters
    for volume names and you do not use absolute paths in your volume
    template.
    """
    ns = spawner.template_namespace()
    ns['username'] = spawner.escaped_name
    return template.format(**ns)

