from kombu import Exchange, Queue
import os

QUEUE_NAME = 'export'

broker_transport = 'redis'
result_backend = 'redis'
# if os.environ.get('SQS'):
#     # Broker settings.
#     broker_transport = 'sqs'
#     broker_transport_options = {
#         'region': 'us-west-2',
#     }
#     assert os.environ.get('QUEUE_PREFIX'), (
#         "Must set 'QUEUE_PREFIX' env variable")
#     prefix = '{}-'.format(os.environ['QUEUE_PREFIX'])
#     broker_transport_options.update(queue_name_prefix=prefix)
#     worker_prefetch_multiplier = 0  # https://github.com/celery/celery/issues/3712  # noqa

# List of modules to import when the Celery worker starts.
imports = ('app.tasks',)

# Configure scheduled tasks to route through exchange
task_track_started = True
task_routes = {
    '*': {'exchange': 'celery', 'routing_key': QUEUE_NAME}
}
default_exchange = Exchange('celery', 'topic')
task_queues = (
    Queue(QUEUE_NAME, default_exchange, routing_key=QUEUE_NAME),
)
