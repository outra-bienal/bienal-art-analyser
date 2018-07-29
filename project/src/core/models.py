from django.db import models
from django.contrib.postgres.fields import JSONField

from proj_utils.redis import RedisAsyncClient
from src.core.tasks import analyse_image_task


class Collection(models.Model):
    title = models.CharField(max_length=200)
    date = models.DateField()


class AnalysedImage(models.Model):
    image = models.ImageField(upload_to='base/')
    recokgnition_result = JSONField(default={}, blank=True)
    job_id = models.CharField(max_length=50, default='', blank=True)

    def enqueue_analysis(self):
        client = RedisAsyncClient()
        job = client.enqueue_default(analyse_image_task, self.id)
        self.job_id = str(job.id)
        self.save(update_fields=['job_id'])
