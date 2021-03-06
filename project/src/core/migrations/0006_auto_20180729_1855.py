# Generated by Django 2.0.6 on 2018-07-29 21:55

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_analysedimage_collection'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='analysedimage',
            options={'verbose_name': 'Análise de Imagem', 'verbose_name_plural': 'Análise de Imagem'},
        ),
        migrations.AlterModelOptions(
            name='collection',
            options={'verbose_name': 'Coleção', 'verbose_name_plural': 'Coleções'},
        ),
        migrations.AlterField(
            model_name='analysedimage',
            name='collection',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='analysed_images', to='core.Collection', verbose_name='Coleção'),
        ),
        migrations.AlterField(
            model_name='analysedimage',
            name='image',
            field=models.ImageField(upload_to='base/', verbose_name='Imagem'),
        ),
        migrations.AlterField(
            model_name='analysedimage',
            name='job_id',
            field=models.CharField(blank=True, default='', max_length=50, verbose_name='Id job de análise'),
        ),
        migrations.AlterField(
            model_name='analysedimage',
            name='recokgnition_result',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default={}, verbose_name='AWS Recokgnition'),
        ),
        migrations.AlterField(
            model_name='collection',
            name='date',
            field=models.DateField(verbose_name='Data'),
        ),
        migrations.AlterField(
            model_name='collection',
            name='title',
            field=models.CharField(max_length=200, verbose_name='Título'),
        ),
    ]
