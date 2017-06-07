from concurrent.futures import ThreadPoolExecutor
import json
from multiprocessing import cpu_count

from django.core.management.base import BaseCommand
from django.db.models import F
from django.db.models.expressions import CombinedExpression, Value
import redis

from tasks.models import BackgroundTask


class Command(BaseCommand):
    help = "Process background task results."

    def add_arguments(self, parser):
        parser.add_argument('-cpu', '--cpu_multiplier', type=int, default=5,
                            help='number of workers per CPU')

    def parse_msg(self, msg):
        # Ignore all but setting keys
        if msg['data'] != b'set':
            err = "ERR: No results found for %r" % msg
            return self.stderr.write(self.style.WARNING(err))

        # Retrieve result
        task_id = msg['channel'].decode("utf-8").split(':')[-1]
        msg = (self.r.get(task_id) or b'').decode("utf-8")
        if not msg:
            err = "ERR: No results found for %r" % task_id
            return self.stderr.write(self.style.ERROR(err))
        self.stdout.write(self.style.SUCCESS(msg))
        return self.add_msg_to_db(json.loads(msg))

    def add_msg_to_db(self, msg):
        # Update DB
        task_qs = BackgroundTask.objects.filter(id=msg['task_id'])
        try:
            assert task_qs.exists()
            self.stdout.write(self.style.SUCCESS('GOOD'))
        except:
            self.stdout.write(self.style.ERROR('BAD'))

        status = msg.get('status')
        if status:
            task_qs.update(status=status)

        result = msg['result']
        if status in BackgroundTask.DONE_STATES:
            task_qs.update(output=result)
        else:
            assert isinstance(result, dict), (
                "Malformed result data, expecting a dict"
            )
            log = result.get('log')
            if log:
                task_qs.update(log=CombinedExpression(
                    F('log'), '||', Value([log])
                ))

    def handle(self, *args, **options):
        self.r = redis.StrictRedis()
        # Ensure we're listening to appropriate events
        assert self.r.config_set('notify-keyspace-events', 'K$')
        pubsub = self.r.pubsub()
        pubsub.psubscribe('__keyspace@*:celery-task-meta-*')

        # Setup Handlers
        worker_count = cpu_count() * options['cpu_multiplier']
        with ThreadPoolExecutor(max_workers=worker_count) as retry_executor:
            with ThreadPoolExecutor(max_workers=worker_count) as executor:
                self.stderr.write(self.style.SUCCESS("Starting..."))
                try:
                    for msg in pubsub.listen():
                        executor.submit(self.parse_msg, msg)
                except KeyboardInterrupt:
                    self.stderr.write(self.style.SUCCESS("Exiting..."))
