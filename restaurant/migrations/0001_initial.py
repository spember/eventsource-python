# Generated by Django 2.1.2 on 2019-01-20 18:49

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(db_index=True, verbose_name='date / time event occurred')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('type', models.CharField(db_index=True, max_length=125, verbose_name='name / key/ for this event')),
                ('event_stream_id', models.UUIDField(db_index=True)),
                ('revision', models.IntegerField(default=0)),
                ('data', django.contrib.postgres.fields.jsonb.JSONField()),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(db_index=True, max_length=100)),
                ('email', models.EmailField(db_index=True, max_length=254, unique=True)),
                ('active', models.BooleanField(db_index=True, default=True)),
            ],
        ),
        migrations.AddField(
            model_name='event',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='restaurant.User'),
        ),
        migrations.AlterUniqueTogether(
            name='event',
            unique_together={('event_stream_id', 'revision')},
        ),
    ]
