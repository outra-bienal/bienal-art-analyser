from unittest.mock import patch, Mock
from model_mommy import mommy

from django.test import TestCase

from .sample_responses import AWS_LABELS_RESPONSE
from src.core.models import AnalysedImage
from src.core.tasks import analyse_image_task


class AnalyseImageTast(TestCase):

    def setUp(self):
        self.analysed_image = mommy.make(AnalysedImage, _create_files=True)

    @patch('src.core.tasks.analysers.aws_analyser')
    def test_populate_recokgnition_result_with_the_output(self, mocked_analyser):
        mocked_analyser.return_value = AWS_LABELS_RESPONSE

        analyse_image_task(self.analysed_image.id)
        self.analysed_image.refresh_from_db()

        assert self.analysed_image.recokgnition_result == AWS_LABELS_RESPONSE
        mocked_analyser.assert_called_once_with(self.analysed_image.image.url)

    @patch('src.core.tasks.analysers.aws_analyser')
    def test_do_not_trigger_recogknition_if_data(self, mocked_analyser):
        self.analysed_image.recokgnition_result = {'foo': 'bar'}
        self.analysed_image.save()

        analyse_image_task(self.analysed_image.id)

        assert mocked_analyser.called is False

    @patch('src.core.tasks.analysers.aws_analyser')
    def test_do_not_update_if_no_result(self, mocked_analyser):
        mocked_analyser.return_value = None

        analyse_image_task(self.analysed_image.id)
        self.analysed_image.refresh_from_db()

        assert self.analysed_image.recokgnition_result == {}
        mocked_analyser.assert_called_once_with(self.analysed_image.image.url)

    @patch('src.core.tasks.analysers.aws_analyser')
    def test_fails_silently_if_no_image(self, mocked_analyser):
        self.analysed_image.delete()
        result = analyse_image_task(self.analysed_image.id)
        assert result is None
