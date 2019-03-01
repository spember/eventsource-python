from abc import ABCMeta, abstractmethod

from django.db import models
from django.contrib.postgres.fields import JSONField


class User(models.Model):
    first_name = models.CharField(max_length=100, null=False)
    last_name = models.CharField(max_length=100, null=False, db_index=True)
    email = models.EmailField(db_index=True, null=False, unique=True)
    active = models.BooleanField(default=True, db_index=True)


class Event(models.Model):
    time = models.DateTimeField('date / time event occurred', db_index=True, null=False)
    # time_recorded = models.DateTimeField('date / time event was recorded', db_index=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, null=False )
    type = models.CharField('name / key/ for this event', max_length=125, db_index=True, null=False)
    event_stream_id = models.UUIDField(null=False, db_index=True)
    revision = models.IntegerField(null=False, default=0)
    data = JSONField(null=False)
    user_id = models.ForeignKey('restaurant.User', db_index=True, null=False, on_delete=models.PROTECT)

    class Meta:
        unique_together = (('event_stream_id', 'revision'),)
