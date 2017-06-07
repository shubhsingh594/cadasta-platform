from kombu import Exchange, Queue

QUEUE_NAME = 'export'
task_default_queue = 'celery'

# List of modules to import when the Celery worker starts.
imports = ('app.tasks',)

broker_transport = 'redis'
result_backend = 'redis'

# Configure scheduled tasks to route through exchange
task_track_started = True
task_routes = {
    '*': {'exchange': task_default_queue, 'routing_key': QUEUE_NAME}
}
default_exchange = Exchange(task_default_queue, 'topic')
task_queues = (
    Queue(QUEUE_NAME, default_exchange, routing_key=QUEUE_NAME),
)
