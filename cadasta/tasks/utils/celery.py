def apply_default_options(options, type):
    """
    Return a copy of task's options with defaults added. Will not
    overwrite existing options' settings.
    """
    from tasks.celery import app

    options = options.copy()
    options.setdefault(
        'queue', app.amqp.router.route({}, type)['queue'].name)
    return options
