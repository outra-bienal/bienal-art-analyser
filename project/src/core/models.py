from unipath import Path

from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils.translation import gettext as _

from proj_utils.redis import RedisAsyncClient
from src.core import tasks


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
    BASE_UPLOAD, YOLO_UPLOAD = 'base/', 'yolo/'

    image = models.ImageField(upload_to=BASE_UPLOAD, verbose_name=_('Imagem'))
    recokgnition_result = JSONField(default={}, blank=True, verbose_name=_('AWS Recokgnition'))
    recokgnition_job_id = models.CharField(max_length=50, default='', blank=True, verbose_name=_('Id job de análise'))
    ibm_watson_result = JSONField(default={}, blank=True, verbose_name=_('IBM Watson'))
    ibm_watson_job_id = models.CharField(max_length=50, default='', blank=True, verbose_name=_('IBM Watson Job'))
    google_vision_result = JSONField(default={}, blank=True, verbose_name=_('AWS Recokgnition'))
    google_vision_job_id = models.CharField(max_length=50, default='', blank=True, verbose_name=_('Google Job'))
    azure_vision_result = JSONField(default={}, blank=True, verbose_name=_('AWS Recokgnition'))
    azure_vision_job_id = models.CharField(max_length=50, default='', blank=True, verbose_name=_('Azure Job'))
    collection = models.ForeignKey(Collection, related_name='analysed_images', on_delete=models.CASCADE, verbose_name=_('Coleção'))
    yolo_image = models.ImageField(upload_to=YOLO_UPLOAD, verbose_name=_('Output YOLO'))
    yolo_job_id = models.CharField(max_length=50, default='', blank=True, verbose_name=_('Yolo Job'))

    @property
    def processed(self):
        return all([
            self.recokgnition_result,
            self.ibm_watson_result,
            self.google_vision_result,
            self.azure_vision_result,
            self.yolo_image,
        ])

    def enqueue_analysis(self):
        client = RedisAsyncClient()

        field_tasks = {
            'recokgnition_result': (tasks.aws_analyse_image_task, 'recokgnition_job_id'),
            'ibm_watson_result': (tasks.ibm_analyse_image_task, 'ibm_watson_job_id'),
            'google_vision_result': (tasks.google_analyse_image_task, 'google_vision_job_id'),
            'azure_vision_result': (tasks.azure_analyse_image_task, 'azure_vision_job_id'),
            'yolo_image': (tasks.yolo_detect_image_task, 'yolo_job_id'),
        }

        update_fields = []
        for fieldname, field_data in field_tasks.items():
            task, job_id_field = field_data
            if not getattr(self, fieldname):
                job = client.enqueue_default(task, self.id)
                setattr(self, job_id_field, str(job.id))
                update_fields.append(job_id_field)

        self.save(update_fields=update_fields)

    def write_image_field(self, image_file):
        """image_file must ben unipath.Path object"""
        name = image_file.name
        with open(image_file, 'rb') as fd:
            self.image.name = self.BASE_UPLOAD + name
            with self.image.open('wb') as out:
                out.write(fd.read())

    def write_yolo_file(self, pred_file):
        """pred_file must ben unipath.Path object"""
        try:
            raw_name = Path(self.image.path).name.split('.')[0]
        except NotImplementedError:
            raw_name = Path(self.image.name).name.split('.')[0]
        ext = pred_file.split('.')[-1]
        out_filename = self.YOLO_UPLOAD + '{}.{}'.format(raw_name, ext)

        with open(pred_file, 'rb') as fd:
            self.yolo_image.name = out_filename
            with self.yolo_image.open('wb') as out:
                out.write(fd.read())

    class Meta:
        verbose_name = _('Análise de Imagem')
        verbose_name_plural = _('Análise de Imagem')
