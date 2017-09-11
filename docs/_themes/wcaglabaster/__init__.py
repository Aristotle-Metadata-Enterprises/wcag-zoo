import os

version = "0.0.1"


def update_context(app, pagename, templatename, context, doctree):
    context['alabaster_version'] = version

def setup(app):
    app.connect('html-page-context', update_context)
    return {'version': version.__version__,
            'parallel_read_safe': True}
