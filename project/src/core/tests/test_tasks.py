from unittest.mock import patch, Mock
from model_mommy import mommy

from django.test import TestCase

from .sample_responses import AWS_LABELS_RESPONSE
from src.core.models import AnalysedImage
from src.core.tasks import aws_analyse_image_task, ibm_analyse_image_task


class AWSAnalyseImageTast(TestCase):

    def setUp(self):
        self.analysed_image = mommy.make(AnalysedImage, _create_files=True)

    @patch('src.core.tasks.analysers.aws_analyser')
    def test_populate_recokgnition_result_with_the_output(self, mocked_analyser):
        mocked_analyser.return_value = AWS_LABELS_RESPONSE

        aws_analyse_image_task(self.analysed_image.id)
        self.analysed_image.refresh_from_db()

        assert self.analysed_image.recokgnition_result == AWS_LABELS_RESPONSE
        mocked_analyser.assert_called_once_with(self.analysed_image.image.url)

    @patch('src.core.tasks.analysers.aws_analyser')
    def test_do_not_update_if_no_result(self, mocked_analyser):
        mocked_analyser.return_value = None

        aws_analyse_image_task(self.analysed_image.id)
        self.analysed_image.refresh_from_db()

        assert self.analysed_image.recokgnition_result == {}
        mocked_analyser.assert_called_once_with(self.analysed_image.image.url)

    @patch('src.core.tasks.analysers.aws_analyser')
    def test_fails_silently_if_no_image(self, mocked_analyser):
        self.analysed_image.delete()
        result = aws_analyse_image_task(self.analysed_image.id)
        assert result is None


class IBMAnalyseImageTast(TestCase):

    def setUp(self):
        self.analysed_image = mommy.make(AnalysedImage, _create_files=True)

    @patch('src.core.tasks.analysers.ibm_analyser')
    def test_populate_ibm_watson_result_with_the_output(self, mocked_analyser):
        mocked_analyser.return_value = {'some': 'data'}

        ibm_analyse_image_task(self.analysed_image.id)
        self.analysed_image.refresh_from_db()

        assert self.analysed_image.ibm_watson_result == {'some': 'data'}
        mocked_analyser.assert_called_once_with(self.analysed_image.image.url)

    @patch('src.core.tasks.analysers.ibm_analyser')
    def test_do_not_update_if_no_result(self, mocked_analyser):
        mocked_analyser.return_value = None

        ibm_analyse_image_task(self.analysed_image.id)
        self.analysed_image.refresh_from_db()

        assert self.analysed_image.ibm_watson_result == {}
        mocked_analyser.assert_called_once_with(self.analysed_image.image.url)

    @patch('src.core.tasks.analysers.ibm_analyser')
    def test_fails_silently_if_no_image(self, mocked_analyser):
        self.analysed_image.delete()
        result = ibm_analyse_image_task(self.analysed_image.id)
        assert result is None
