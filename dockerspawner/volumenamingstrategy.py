class VolumeNamingStrategy():
    """The default behavior used to name user volumes for Jupyter Docker containers.
       
       {username} template variables in label_template will be substituted by the
       user's name.
    """
    def name_volume(self, label_template, spawner):
        return label_template.format(username=spawner.user.name)


