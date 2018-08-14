from unittest.mock import patch, Mock
from model_mommy import mommy

from django.test import TestCase

from .sample_responses import AWS_LABELS_RESPONSE
from src.core.models import AnalysedImage
from src.core.tasks import aws_analyse_image_task, ibm_analyse_image_task, google_analyse_image_task, azure_analyse_image_task, deep_ai_analyse_image_task


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


class GoogleAnalyseImageTast(TestCase):

    def setUp(self):
        self.analysed_image = mommy.make(AnalysedImage, _create_files=True)

    @patch('src.core.tasks.analysers.google_analyser')
    def test_populate_google_watson_result_with_the_output(self, mocked_analyser):
        mocked_analyser.return_value = {'some': 'data'}

        google_analyse_image_task(self.analysed_image.id)
        self.analysed_image.refresh_from_db()

        assert self.analysed_image.google_vision_result == {'some': 'data'}
        mocked_analyser.assert_called_once_with(self.analysed_image.image.url)

    @patch('src.core.tasks.analysers.google_analyser')
    def test_do_not_update_if_no_result(self, mocked_analyser):
        mocked_analyser.return_value = None

        google_analyse_image_task(self.analysed_image.id)
        self.analysed_image.refresh_from_db()

        assert self.analysed_image.google_vision_result == {}
        mocked_analyser.assert_called_once_with(self.analysed_image.image.url)

    @patch('src.core.tasks.analysers.google_analyser')
    def test_fails_silently_if_no_image(self, mocked_analyser):
        self.analysed_image.delete()
        result = google_analyse_image_task(self.analysed_image.id)
        assert result is None


class AzureAnalyseImageTast(TestCase):

    def setUp(self):
        self.analysed_image = mommy.make(AnalysedImage, _create_files=True)

    @patch('src.core.tasks.analysers.azure_analyser')
    def test_populate_azure_vision_result_with_the_output(self, mocked_analyser):
        mocked_analyser.return_value = {'some': 'data'}

        azure_analyse_image_task(self.analysed_image.id)
        self.analysed_image.refresh_from_db()

        assert self.analysed_image.azure_vision_result == {'some': 'data'}
        mocked_analyser.assert_called_once_with(self.analysed_image.image.url)

    @patch('src.core.tasks.analysers.azure_analyser')
    def test_do_not_update_if_no_result(self, mocked_analyser):
        mocked_analyser.return_value = None

        azure_analyse_image_task(self.analysed_image.id)
        self.analysed_image.refresh_from_db()

        assert self.analysed_image.azure_vision_result == {}
        mocked_analyser.assert_called_once_with(self.analysed_image.image.url)

    @patch('src.core.tasks.analysers.azure_analyser')
    def test_fails_silently_if_no_image(self, mocked_analyser):
        self.analysed_image.delete()
        result = azure_analyse_image_task(self.analysed_image.id)
        assert result is None


class DeepAiAnalyseImageTast(TestCase):

    def setUp(self):
        self.analysed_image = mommy.make(AnalysedImage, _create_files=True)

    @patch('src.core.tasks.analysers.deep_ai_analyser')
    def test_populate_deep_ai_result_with_the_output(self, mocked_analyser):
        mocked_analyser.return_value = {'some': 'data'}

        deep_ai_analyse_image_task(self.analysed_image.id)
        self.analysed_image.refresh_from_db()

        assert self.analysed_image.deep_ai_result == {'some': 'data'}
        mocked_analyser.assert_called_once_with(self.analysed_image.image.url)

    @patch('src.core.tasks.analysers.deep_ai_analyser')
    def test_do_not_update_if_no_result(self, mocked_analyser):
        mocked_analyser.return_value = None

        deep_ai_analyse_image_task(self.analysed_image.id)
        self.analysed_image.refresh_from_db()

        assert self.analysed_image.deep_ai_result == {}
        mocked_analyser.assert_called_once_with(self.analysed_image.image.url)

    @patch('src.core.tasks.analysers.deep_ai_analyser')
    def test_fails_silently_if_no_image(self, mocked_analyser):
        self.analysed_image.delete()
        result = deep_ai_analyse_image_task(self.analysed_image.id)
        assert result is None
