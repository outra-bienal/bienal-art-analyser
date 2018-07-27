from django.db import models


class AnalysedImage(models.Model):
    image = models.ImageField(upload_to='base/')
