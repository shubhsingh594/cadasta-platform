# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-09-13 05:41
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import functools
import tasks.fields
import tasks.utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BackgroundTask',
            fields=[
                ('id', models.CharField(max_length=24, primary_key=True, serialize=False)),
                ('task_id', models.CharField(editable=False, max_length=155, unique=True, verbose_name='UUID')),
                ('type', models.CharField(max_length=128, verbose_name='Task function')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('input', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=tasks.utils.fields.input_field_default, validators=[functools.partial(tasks.utils.fields.validate_type, *(dict,), **{}), tasks.utils.fields.validate_input_field])),
                ('options', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, validators=[functools.partial(tasks.utils.fields.validate_type, *(dict,), **{})], verbose_name='Task scheduling options')),
                ('related_object_id', models.CharField(blank=True, max_length=24, null=True)),
                ('immutable', models.NullBooleanField(verbose_name='If arguments are immutable (only applies to chained tasks).')),
                ('creator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='tasks.BackgroundTask', to_field='task_id')),
                ('related_content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='contenttypes.ContentType')),
                ('root', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='descendents', to='tasks.BackgroundTask', to_field='task_id')),
            ],
            options={
                'ordering': ['created_date'],
            },
        ),
        migrations.CreateModel(
            name='TaskResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(max_length=50, verbose_name='State')),
                ('result', tasks.fields.PickledObjectField(null=True)),
                ('date_done', models.DateTimeField(null=True)),
                ('traceback', models.TextField(null=True)),
                ('task', models.OneToOneField(db_constraint=False, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='result', to='tasks.BackgroundTask', to_field='task_id')),
            ],
            options={
                'db_table': 'celery_taskmeta',
            },
        ),
    ]
