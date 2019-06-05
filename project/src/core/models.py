from unipath import Path

from django.contrib.postgres.fields import JSONField
from django.core.cache import cache
from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import gettext as _

from proj_utils.redis import RedisAsyncClient
from src.core import tasks


class CollectionQuerySet(models.QuerySet):

    def public(self):
        return self.filter(public=True)


class Collection(models.Model):
    objects = CollectionQuerySet.as_manager()

    title = models.CharField(max_length=200, verbose_name=_('Título da Coleção'))
    date = models.DateField(verbose_name=_('Data'))
    public = models.BooleanField(default=True, verbose_name=_('Coleção Pública'))

    def run_analysis(self):
        for image in self.analysed_images.all():
            if not image.processed:
                image.enqueue_analysis()

    def generate_dense_cap_images(self):
        for image in self.analysed_images.all():
            image.enqueue_dense_cap_image()

    @property
    def processed(self):
        return all([i.processed for i in self.analysed_images.all()])

    class Meta:
        verbose_name = _('Coleção')
        verbose_name_plural = _('Coleções')


class AnalysedImage(models.Model):
    BASE_UPLOAD = 'base/'
    YOLO_UPLOAD = 'yolo/'
    DETECTRON_UPLOAD = 'detectron/'
    DENSE_CAP_UPLOAD = 'dense_cap/'

    collection = models.ForeignKey(Collection, related_name='analysed_images', on_delete=models.CASCADE, verbose_name=_('Coleção'))
    image = models.ImageField(upload_to=BASE_UPLOAD, verbose_name=_('Imagem'))
    recokgnition_result = JSONField(default=dict, blank=True, verbose_name=_('AWS Recokgnition'))
    recokgnition_job_id = models.CharField(max_length=50, default='', blank=True, verbose_name=_('Id job de análise'))
    ibm_watson_result = JSONField(default=dict, blank=True, verbose_name=_('IBM Watson'))
    ibm_watson_job_id = models.CharField(max_length=50, default='', blank=True, verbose_name=_('IBM Watson Job'))

    google_vision_result = JSONField(default=dict, blank=True, verbose_name=_('AWS Recokgnition'))
    google_vision_job_id = models.CharField(max_length=50, default='', blank=True, verbose_name=_('Google Job'))

    azure_vision_result = JSONField(default=dict, blank=True, verbose_name=_('AWS Recokgnition'))
    azure_vision_job_id = models.CharField(max_length=50, default='', blank=True, verbose_name=_('Azure Job'))

    deep_ai_result = JSONField(default=dict, blank=True, verbose_name=_('Deep AI'))
    deep_ai_job_id = models.CharField(max_length=50, default='', blank=True, verbose_name=_('Deep AI Job'))

    clarifai_result = JSONField(default=dict, blank=True, verbose_name=_('Clarifai'))
    clarifai_job_id = models.CharField(max_length=50, default='', blank=True, verbose_name=_('Clarifai Job'))

    detectron_image = models.ImageField(upload_to=DETECTRON_UPLOAD, verbose_name=_('Output Detectron'), null=True)

    yolo_image = models.ImageField(upload_to=YOLO_UPLOAD, verbose_name=_('Output YOLO'))
    yolo_job_id = models.CharField(max_length=50, default='', blank=True, verbose_name=_('Yolo Job'))

    dense_cap_image = models.ImageField(upload_to=DENSE_CAP_UPLOAD, verbose_name=('Output Dense Cap (10 results)'), null=True)
    dense_cap_full_image = models.ImageField(upload_to=DENSE_CAP_UPLOAD, verbose_name=('Output Dense Cap (all results)'), null=True)
    dense_cap_job_id = models.CharField(max_length=50, default='', blank=True, verbose_name=_('Dense Cap Job'))

    @property
    def processed(self):
        return all([
            self.recokgnition_result,
            self.ibm_watson_result,
            self.google_vision_result,
            self.azure_vision_result,
            self.deep_ai_result,
            self.yolo_image,
            self.clarifai_result,
        ])

    def enqueue_analysis(self):
        client = RedisAsyncClient()

        field_tasks = {
            'recokgnition_result': (tasks.aws_analyse_image_task, 'recokgnition_job_id'),
            'ibm_watson_result': (tasks.ibm_analyse_image_task, 'ibm_watson_job_id'),
            'google_vision_result': (tasks.google_analyse_image_task, 'google_vision_job_id'),
            'azure_vision_result': (tasks.azure_analyse_image_task, 'azure_vision_job_id'),
            'deep_ai_result': (tasks.deep_ai_analyse_image_task, 'deep_ai_job_id'),
            'clarifai_result': (tasks.clarifai_analyse_image_task, 'clarifai_job_id'),
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

    def process_analysis(self):
        field_tasks = {
            'recokgnition_result': (tasks.aws_analyse_image_task, 'recokgnition_job_id'),
            'ibm_watson_result': (tasks.ibm_analyse_image_task, 'ibm_watson_job_id'),
            'google_vision_result': (tasks.google_analyse_image_task, 'google_vision_job_id'),
            'azure_vision_result': (tasks.azure_analyse_image_task, 'azure_vision_job_id'),
            'deep_ai_result': (tasks.deep_ai_analyse_image_task, 'deep_ai_job_id'),
            'clarifai_result': (tasks.clarifai_analyse_image_task, 'clarifai_job_id'),
            'yolo_image': (tasks.yolo_detect_image_task, 'yolo_job_id'),
        }

        for fieldname, field_data in field_tasks.items():
            if not getattr(self, fieldname):
                task, job_id_field = field_data
                task(self.id)

    def enqueue_dense_cap_image(self):
        if 'DenseCap' not in self.deep_ai_result:
            return

        client = RedisAsyncClient()
        job = client.enqueue_default(tasks.generate_dense_cap_image_task, self.id)
        self.dense_cap_job_id = str(job.id)
        self.save(update_fields=['dense_cap_job_id'])

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

    def write_detectron_field(self, image_file):
        """image_file must ben unipath.Path object"""
        name = image_file.name
        with open(image_file, 'rb') as fd:
            self.detectron_image.name = self.DETECTRON_UPLOAD + name
            with self.detectron_image.open('wb') as out:
                out.write(fd.read())

    def write_dense_cap_image(self, image_file):
        """image_file must ben unipath.Path object"""
        name = image_file.name
        with open(image_file, 'rb') as fd:
            self.dense_cap_image.name = self.DENSE_CAP_UPLOAD + name
            with self.dense_cap_image.open('wb') as out:
                out.write(fd.read())

    def write_dense_cap_full_image(self, image_file):
        """image_file must ben unipath.Path object"""
        name = image_file.name
        with open(image_file, 'rb') as fd:
            name = 'full_' + name
            self.dense_cap_full_image.name = self.DENSE_CAP_UPLOAD + name
            with self.dense_cap_full_image.open('wb') as out:
                out.write(fd.read())

    class Meta:
        verbose_name = _('Análise de Imagem')
        verbose_name_plural = _('Análise de Imagem')
        ordering = ['image']


def clear_cache(sender, instance, **kwargs):
    cache.clear()


post_save.connect(clear_cache, sender=Collection)
post_save.connect(clear_cache, sender=AnalysedImage)
