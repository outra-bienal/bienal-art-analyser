# Generated by Django 2.0.8 on 2019-05-13 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_collection_public'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='triggered_analysis',
            field=models.BooleanField(default=False),
        ),
    ]
