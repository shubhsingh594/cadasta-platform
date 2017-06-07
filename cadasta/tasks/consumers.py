import logging

from celery import bootsteps


from .models import BackgroundTask


logger = logging.getLogger(__name__)


def process_message(message):
    """ Add scheduled tasks to database """
    try:
        args, kwargs, options = message.decode()
        task_id = message.headers['id']

        # Add default properties
        option_keys = ['eta', 'expires', 'retries', 'timelimit']
        message.properties.update(
            **{k: v for k, v in message.headers.items()
               if k in option_keys and v not in (None, [None, None])})

        # Ensure chained followup tasks contain proper data
        chain_parent_id = task_id[:]
        chain = options.get('chain') or []
        for t in chain[::-1]:  # Chain array comes in reverse order
            t['parent_id'] = chain_parent_id
            chain_parent_id = t['options']['task_id']

        if message.headers['parent_id'] == 'ID_hello_suzy':
            print('headers', message.headers)
            print('props', message.properties)
            print('message', message)
            # from celery.contrib import rdb
            # rdb.set_trace()

        # TODO: Add support for grouped tasks
        # TODO: Add support tasks gednerated by workers
        _, created = BackgroundTask.objects.get_or_create(
            id=task_id,
            defaults={
                'type': message.headers['task'],
                'input_args': args,
                'input_kwargs': kwargs,
                'options': message.properties,
                'parent_id': message.headers['parent_id'],
                'root_id': message.headers['root_id'],
            }
        )
        if created:
            logger.debug("Processed message: %r", message)
        else:
            logger.warn("Message already existed in db: %r", message)
    except Exception as e:
        should_requeue = message._state != 'REQUEUED'
        try:
            msg = "Failed to process message"
            if should_requeue:
                message.requeue()
                logger.warn("%s, requeued: %s, %r", msg, e, message)
            else:
                logger.exception("%s, not requeued: %r", msg, message)
        except:
            logger.exception("Failed to requeue: %r", message)
            message.ack()
    else:
        message.ack()


class ResultConsumer(bootsteps.ConsumerStep):
    """
    Reads off the Result queue, inserting messages into DB.

    NOTE: This only works if you run a celery worker that is NOT looking
    at the Result queue. Ex. "celery -A config worker"
    """

    def __init__(self, consumer, *args, **kwargs):
        # Override parent consumer
        consumer.create_task_handler = lambda: process_message
        super(ResultConsumer, self).__init__(consumer, *args, **kwargs)

    def get_consumers(self, channel):
        return []

    def handle_message(self, body, message):
        pass
