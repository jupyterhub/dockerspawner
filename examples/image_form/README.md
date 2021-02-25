# Options form to select custom images

This example configures JupyterHub to allow users to launch arbitrary docker images, selected via an options_form.

There are 3 steps:

1. enable an `options_form`. This can be a simple bootstrap html form snippet,
   or a *callable* that takes the Spawner instance and returns such a form.
   In this case, we create one `input` element with a `label`,
   making sure to apply bootstrap's `form-control` class.
2. define `Spawner.options_from_form(formdata)` to transform the form data (always a dict of lists of strings, e.g. `{"image": ["string"]}`) into the expected dictionary structure
3. define `Spawner.load_user_options` to take the dict returned by `options_from_form` and modify the Spawner. In this case, that's setting `self.image` if `image` is in the specified options

To run the example, in this directory type:

```bash
jupyterhub
```

and visit `http://localhost:8000`. Dummy auth is enabled, so any username+password will work.
