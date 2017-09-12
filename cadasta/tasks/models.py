from celery import states
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.db import models, transaction
from django.db.models.expressions import F
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import lazy

from core.util import ID_FIELD_LENGTH
from core.models import RandomIDModel

from .celery import app
from .utils import fields as utils
from .fields import PickledObjectField


choices = lazy(lambda: [
    (t, t) for t in sorted(app.tasks.keys())
    if not t.startswith('celery.')], list)


class TaskResult(models.Model):
    ALL_STATES = sorted(states.ALL_STATES)
    DONE_STATES = ('SUCCESS', 'FAILURE')
    TASK_STATE_CHOICES = sorted(zip(ALL_STATES, ALL_STATES))

    task = models.OneToOneField(
        'BackgroundTask', to_field='task_id', db_constraint=False,
        editable=False, null=True, related_name='result')
    status = models.CharField(_('State'), max_length=50)
    result = PickledObjectField(null=True)
    date_done = models.DateTimeField(null=True)
    traceback = models.TextField(null=True)

    def __str__(self):
        return 'task={0.task_id} status={0.status}'.format(self)

    class Meta:
        db_table = 'celery_taskmeta'


class BackgroundTask(RandomIDModel):

    task_id = models.CharField(
        _('UUID'), max_length=155, unique=True,
        editable=False)

    type = models.CharField(
        _('Task function'), max_length=128,
        choices=choices())

    created_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True)

    input = JSONField(
        default=utils.input_field_default, blank=True,
        validators=[utils.is_type(dict), utils.validate_input_field])
    options = JSONField(
        _('Task scheduling options'), default=dict, blank=True,
        validators=[utils.is_type(dict)])

    related_content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, related_name='+',
        null=True, blank=True)
    related_object_id = models.CharField(
        max_length=ID_FIELD_LENGTH, null=True, blank=True)
    related_object = GenericForeignKey(
        'related_content_type', 'related_object_id')

    parent = models.ForeignKey(
        'self', related_name='children', to_field='task_id',
        on_delete=models.CASCADE, blank=True, null=True)
    root = models.ForeignKey(
        'self', related_name='descendents', to_field='task_id',
        on_delete=models.CASCADE, blank=True, null=True)
    immutable = models.NullBooleanField(
        _("If arguments are immutable (only applies to chained tasks)."))

    class Meta:
        ordering = ['created_date']

    def __str__(self):
        return 'id={0.id} type={0.type} status={0.status}'.format(self)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            super().save(*args, **kwargs)
            # Ensure model fields run through validators after special
            # auto-filled data (eg auto_now_add) is added.
            self.full_clean(exclude=None)

    @property
    def status(self):
        try:
            return self.result.status
        except TaskResult.DoesNotExist:
            return 'PENDING'

    @property
    def input_args(self):
        return self.input.get('args')

    @input_args.setter
    def input_args(self, value):
        self.input['args'] = value

    @property
    def input_kwargs(self):
        return self.input.get('kwargs')

    @input_kwargs.setter
    def input_kwargs(self, value):
        self.input['kwargs'] = value

    @property
    def overall_status(self):
        tasks = self.descendents.exclude(type='celery.chord_unlock')
        tasks = tasks.annotate(_status=F('result__status')).order_by('_status')
        statuses = tasks.values_list('_status', flat=True).distinct()
        if len(statuses) == 1:
            # It's possible for all statuses to equal None, in which case we
            # can call them 'PENDING'
            return statuses[0] or 'PENDING'
        if 'FAILURE' in statuses:
            return 'FAILURE'
        return 'STARTED'

    @property
    def overall_results(self):
        results = self.descendents.filter(options__is_result=True)
        return results.values_list('result__result', flat=True)

        # test:
        #  - 2 tasks, one success and other no results. 'STARTED'
        #  - 2 tasks, one success and other failed. 'FAILURE'
        #  - 1 task, no results. 'PENDING'