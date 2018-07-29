from django.db import models
from django.contrib.postgres.fields import JSONField


class AnalysedImage(models.Model):
    image = models.ImageField(upload_to='base/')
    recokgnition_result = JSONField(default={}, blank=True)
    job_id = models.CharField(max_length=50, default='', blank=True)
