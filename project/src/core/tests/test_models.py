from model_mommy import mommy
from unittest.mock import patch, Mock

from django.test import TestCase

from src.core.models import AnalysedImage
from src.core.tasks import analyse_image_task
from proj_utils.redis import RedisAsyncClient


class AnalysedImageModelTests(TestCase):

    def setUp(self):
        self.analysed_image = mommy.make(AnalysedImage)

    @patch.object(RedisAsyncClient, 'enqueue_default', Mock(id=42))
    def test_enqueue_analysis(self):
        client = RedisAsyncClient()

        self.analysed_image.enqueue_analysis()
        self.analysed_image.refresh_from_db()

        client.enqueue_default.assert_called_once_with(
            analyse_image_task, self.analysed_image.id
        )
        self.analysed_image.job_id = '42'
