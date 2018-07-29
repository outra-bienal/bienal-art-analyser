# Generated by Django 2.0.6 on 2018-07-29 21:12

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_analysedimage_recokgnition_result'),
    ]

    operations = [
        migrations.AddField(
            model_name='analysedimage',
            name='job_id',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='analysedimage',
            name='recokgnition_result',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default={}),
        ),
    ]