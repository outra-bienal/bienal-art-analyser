from model_mommy import mommy
from unittest.mock import patch, Mock

from django.test import TestCase

from src.core import tasks
from src.core.models import AnalysedImage
from proj_utils.redis import RedisAsyncClient


class AnalysedImageModelTests(TestCase):

    def setUp(self):
        self.analysed_image = mommy.make(
            AnalysedImage,
            recokgnition_result={'fake': 'data'},
            ibm_watson_result={'fake': 'data'},
            google_vision_result={'fake': 'data'},
            azure_vision_result={'fake': 'data'},
            deep_ai_result={'fake': 'data'},
            _create_files=True,
        )

    def tearDown(self):
        self.analysed_image.image.delete()
        if self.analysed_image.yolo_image:
            self.analysed_image.yolo_image.delete()
        if self.analysed_image.detectron_image:
            self.analysed_image.detectron_image.delete()

    @patch.object(RedisAsyncClient, 'enqueue_default', Mock(id=42))
    def test_do_not_enqueue_if_data(self):
        client = RedisAsyncClient()

        self.analysed_image.enqueue_analysis()

        assert client.enqueue_default.called is False

    @patch.object(RedisAsyncClient, 'enqueue_default', Mock(id=42))
    def test_enqueue_aws_analysis(self):
        self.analysed_image.recokgnition_result = {}
        self.analysed_image.save()
        client = RedisAsyncClient()

        self.analysed_image.enqueue_analysis()
        self.analysed_image.refresh_from_db()

        client.enqueue_default.assert_called_once_with(
            tasks.aws_analyse_image_task, self.analysed_image.id
        )
        self.analysed_image.recokgnition_job_id = '42'

    @patch.object(RedisAsyncClient, 'enqueue_default', Mock(id=42))
    def test_enqueue_ibm_analysis(self):
        self.analysed_image.ibm_watson_result = {}
        self.analysed_image.save()
        client = RedisAsyncClient()

        self.analysed_image.enqueue_analysis()
        self.analysed_image.refresh_from_db()

        client.enqueue_default.assert_called_once_with(
            tasks.ibm_analyse_image_task, self.analysed_image.id
        )
        self.analysed_image.ibm_watson_job_id = '42'

    @patch.object(RedisAsyncClient, 'enqueue_default', Mock(id=42))
    def test_enqueue_google_analysis(self):
        self.analysed_image.google_vision_result = {}
        self.analysed_image.save()
        client = RedisAsyncClient()

        self.analysed_image.enqueue_analysis()
        self.analysed_image.refresh_from_db()

        client.enqueue_default.assert_called_once_with(
            tasks.google_analyse_image_task, self.analysed_image.id
        )
        self.analysed_image.google_vision_job_id = '42'

    @patch.object(RedisAsyncClient, 'enqueue_default', Mock(id=42))
    def test_enqueue_azure_analysis(self):
        self.analysed_image.azure_vision_result = {}
        self.analysed_image.save()
        client = RedisAsyncClient()

        self.analysed_image.enqueue_analysis()
        self.analysed_image.refresh_from_db()

        client.enqueue_default.assert_called_once_with(
            tasks.azure_analyse_image_task, self.analysed_image.id
        )
        self.analysed_image.azure_vision_job_id = '42'

    @patch.object(RedisAsyncClient, 'enqueue_default', Mock(id=42))
    def test_enqueue_deep_ai_analysis(self):
        self.analysed_image.deep_ai_result = {}
        self.analysed_image.save()
        client = RedisAsyncClient()

        self.analysed_image.enqueue_analysis()
        self.analysed_image.refresh_from_db()

        client.enqueue_default.assert_called_once_with(
            tasks.deep_ai_analyse_image_task, self.analysed_image.id
        )
        self.analysed_image.deep_ai_job_id = '42'

    @patch.object(RedisAsyncClient, 'enqueue_default', Mock(id=42))
    def test_enqueue_yolo_detection(self):
        self.analysed_image.yolo_image.delete()
        self.analysed_image.save()
        client = RedisAsyncClient()

        self.analysed_image.enqueue_analysis()
        self.analysed_image.refresh_from_db()

        client.enqueue_default.assert_called_once_with(
            tasks.yolo_detect_image_task, self.analysed_image.id
        )
        self.analysed_image.yolo_job_id = '42'

    def test_processed_tag(self):
        assert self.analysed_image.processed is True
        self.analysed_image.recokgnition_result = {}
        assert self.analysed_image.processed is False
        self.analysed_image.recokgnition_result = {'foo': 'bar'}
        self.analysed_image.ibm_watson_result = {}
        assert self.analysed_image.processed is False
        self.analysed_image.ibm_watson_result = {'foo': 'bar'}
        self.analysed_image.google_vision_result = {}
        assert self.analysed_image.processed is False
        self.analysed_image.google_vision_result = {'foo': 'bar'}
        self.analysed_image.azure_vision_result = {}
        assert self.analysed_image.processed is False
        self.analysed_image.azure_vision_result = {'foo': 'bar'}
        self.analysed_image.deep_ai_result = {}
        assert self.analysed_image.processed is False
        self.analysed_image.deep_ai_result = {'foo': 'bar'}
        self.analysed_image.yolo_image.delete()
        assert self.analysed_image.processed is False
