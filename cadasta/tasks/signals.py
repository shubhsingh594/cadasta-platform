from celery.signals import before_task_publish

from .utils.celery import apply_default_options

# TOOO: This is no longer needed, all routing provided by exchange
@before_task_publish.connect
def route_chained_task(sender, headers, body, properties, **kw):
    """
    Ensure tasks in chains and chords are properly routed before being
    scheduled.
    """
    _, _, opts = body

    # Ensure chained followup tasks contain proper data
    for t in (opts.get('chain') or []):
        print(t.options)
        import pudb; pu.db
        t.options = apply_default_options(t.options, t.name)
        print(t.options)

    if opts.get('chord'):
        chordopts = opts['chord']['options']
        chordtask = opts['chord']['task']
        opts['chord']['options'] = apply_default_options(chordopts, chordtask)
