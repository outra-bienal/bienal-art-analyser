from unittest.mock import Mock, patch
from watson_developer_cloud import VisualRecognitionV3

from django.conf import settings
from django.test import TestCase

from .sample_responses import *
from src.core.analysers import aws_analyser, ibm_analyser


class TestAWSAnalyser(TestCase):
    image_url = 'https://bienal-image-analyser.s3.amazonaws.com/folder/img.jpg?X-Amz-Algorithm=AWS4-HMAC'

    @patch('src.core.analysers.boto3')
    def test_return_response_if_success(self, MockedBoto3):
        client = Mock()
        client.detect_labels.return_value = AWS_LABELS_RESPONSE
        client.detect_faces.return_value = AWS_FACES_RESPONSE
        client.recognize_celebrities.return_value = AWS_CELEBRITIES_RESPONSE
        MockedBoto3.client.return_value = client

        data = aws_analyser(self.image_url)
        expected = {
            'labels': AWS_LABELS_RESPONSE,
            'faces': AWS_FACES_RESPONSE,
            'celebs': AWS_CELEBRITIES_RESPONSE,
        }

        assert expected == data
        MockedBoto3.client.assert_called_once_with(
            'rekognition',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        kwargs = {'Image': {
            'S3Object': {
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Name': 'folder/img.jpg'
            }
        }}
        client.detect_labels.assert_called_once_with(**kwargs)
        client.detect_faces.assert_called_once_with(**kwargs)
        client.recognize_celebrities.assert_called_once_with(**kwargs)

    @patch('src.core.analysers.boto3')
    def test_return_none_if_any_error(self, MockedBoto3):
        client = Mock()
        client.detect_labels.side_effect = Exception
        MockedBoto3.client.return_value = client

        data = aws_analyser(self.image_url)

        assert data is None


class TestIBMAnalyser(TestCase):
    image_url = 'https://bienal-image-analyser.s3.amazonaws.com/folder/img.jpg?X-Amz-Algorithm=AWS4-HMAC'

    @patch('src.core.analysers.VisualRecognitionV3')
    def test_return_response_if_success(self, MockedVisualRecognitionV3):
        client = Mock(VisualRecognitionV3)
        client.classify.return_value = IBM_CLASSIFY_RESPONSE
        MockedVisualRecognitionV3.return_value = client

        clean_url = 'https://bienal-image-analyser.s3.amazonaws.com/folder/img.jpg'
        data = ibm_analyser(self.image_url)
        expected = {
            'main': IBM_CLASSIFY_RESPONSE['images'][0],
            'faces': {},
        }

        assert expected == data
        MockedVisualRecognitionV3.assert_called_once_with(
            settings.IBM_WATSON_VISUAL_RECOG_VERSION,
            iam_api_key=settings.IBM_IAM_API_KEY
        )
        kwargs = {'url': clean_url}
        client.classify.assert_called_once_with(**kwargs)

    @patch('src.core.analysers.VisualRecognitionV3')
    def test_return_none_if_any_error(self, MockedVisualRecognitionV3):
        client = Mock(VisualRecognitionV3)
        client.classify.side_effect = Exception
        MockedVisualRecognitionV3.return_value = client

        data = ibm_analyser(self.image_url)

        assert data is None
