from django.apps import AppConfig


class TasksConfig(AppConfig):
    name = 'tasks'

    def ready(self):
        from . import signals  # NOQA
        from .celery import app
        from .consumers import ResultConsumer
        app.steps['consumer'].add(ResultConsumer)
        app.autodiscover_tasks(force=True)

        # Ensure exchange is set up with all queues
        p = app.amqp.producer_pool.acquire()
        try:
            [p.maybe_declare(q) for q in app.amqp.queues.values()]
        finally:
            p.release()
