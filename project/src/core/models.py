from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils.translation import gettext as _

from proj_utils.redis import RedisAsyncClient
from src.core.tasks import analyse_image_task


class Collection(models.Model):
    title = models.CharField(max_length=200, verbose_name=_('Título da Coleção'))
    date = models.DateField(verbose_name=_('Data'))

    def run_analysis(self):
        for image in self.analysed_images.all():
            if not image.processed:
                image.enqueue_analysis()

    @property
    def processed(self):
        return all([i.processed for i in self.analysed_images.all()])

    class Meta:
        verbose_name = _('Coleção')
        verbose_name_plural = _('Coleções')


class AnalysedImage(models.Model):
    image = models.ImageField(upload_to='base/', verbose_name=_('Imagem'))
    recokgnition_result = JSONField(default={}, blank=True, verbose_name=_('AWS Recokgnition'))
    job_id = models.CharField(max_length=50, default='', blank=True, verbose_name=_('Id job de análise'))
    collection = models.ForeignKey(Collection, related_name='analysed_images', on_delete=models.CASCADE, verbose_name=_('Coleção'))

    @property
    def processed(self):
        return bool(self.recokgnition_result)

    def enqueue_analysis(self):
        client = RedisAsyncClient()
        job = client.enqueue_default(analyse_image_task, self.id)
        self.job_id = str(job.id)
        self.save(update_fields=['job_id'])

    class Meta:
        verbose_name = _('Análise de Imagem')
        verbose_name_plural = _('Análise de Imagem')
