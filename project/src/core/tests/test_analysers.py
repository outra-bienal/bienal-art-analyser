import pytest
from urllib.parse import urlencode
import json
import responses
from unittest.mock import Mock, patch
from watson_developer_cloud import VisualRecognitionV3
from clarifai.rest import ClarifaiApp

from django.conf import settings
from django.test import TestCase

from .sample_responses import *
from src.core.analysers import aws_analyser, ibm_analyser, google_analyser, azure_analyser, deep_ai_analyser, AnalysisError


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
    def test_raise_exception_if_any_error(self, MockedBoto3):
        client = Mock()
        client.detect_labels.side_effect = Exception
        MockedBoto3.client.return_value = client

        with pytest.raises(AnalysisError):
            aws_analyser(self.image_url)


class TestIBMAnalyser(TestCase):
    image_url = 'https://bienal-image-analyser.s3.amazonaws.com/folder/img.jpg?X-Amz-Algorithm=AWS4-HMAC'

    @patch('src.core.analysers.VisualRecognitionV3')
    def test_return_response_if_success(self, MockedVisualRecognitionV3):
        client = Mock(VisualRecognitionV3)
        client.classify.return_value = IBM_CLASSIFY_RESPONSE
        client.detect_faces.return_value = IBM_FACES_RESPONSE
        MockedVisualRecognitionV3.return_value = client

        clean_url = 'https://bienal-image-analyser.s3.amazonaws.com/folder/img.jpg'
        face_params = json.dumps({'url': clean_url})
        data = ibm_analyser(self.image_url)
        expected = {
            'main': IBM_CLASSIFY_RESPONSE['images'][0],
            'faces': IBM_FACES_RESPONSE['images'][0],
        }

        assert expected == data
        MockedVisualRecognitionV3.assert_called_once_with(
            settings.IBM_WATSON_VISUAL_RECOG_VERSION,
            iam_api_key=settings.IBM_IAM_API_KEY
        )
        kwargs = {'url': clean_url}
        client.classify.assert_called_once_with(**kwargs)
        client.detect_faces.assert_called_once_with(parameters=face_params)

    @patch('src.core.analysers.VisualRecognitionV3')
    def test_raise_exception_if_any_error(self, MockedVisualRecognitionV3):
        client = Mock(VisualRecognitionV3)
        client.classify.side_effect = Exception
        MockedVisualRecognitionV3.return_value = client

        with pytest.raises(AnalysisError):
            ibm_analyser(self.image_url)


class TestGoogleAnalyser(TestCase):
    image_url = 'https://bienal-image-analyser.s3.amazonaws.com/folder/img.jpg?X-Amz-Algorithm=AWS4-HMAC'

    @responses.activate
    def test_return_response_if_success(self):
        url = 'https://vision.googleapis.com/v1/images:annotate?key={}'.format(settings.GOOGLE_VISION_API_KEY)
        responses.add(
            responses.POST,
            url,
            json=GOOGLE_ANNOTATE_RESPONSE,
            status=200,
            match_querystring=True
        )

        clean_url = 'https://bienal-image-analyser.s3.amazonaws.com/folder/img.jpg'
        data = google_analyser(self.image_url)
        expected_request = {
            "image": {"source": {"imageUri": clean_url}},
            "features": [
                {"type": "FACE_DETECTION"},
                {"type": "LABEL_DETECTION"},
                {"type": "LANDMARK_DETECTION"},
                {"type": "WEB_DETECTION"},
                {"type": "IMAGE_PROPERTIES"},
                {"type": "SAFE_SEARCH_DETECTION"},
                {"type": "DOCUMENT_TEXT_DETECTION"}
            ]
        }

        json_data = json.loads(responses.calls[0].request.body)
        assert GOOGLE_ANNOTATE_RESPONSE['responses'][0] == data
        assert {'requests': [expected_request]} == json_data

    @responses.activate
    def test_raise_exception_if_any_error(self):
        url = 'https://vision.googleapis.com/v1/images:annotate?key={}'.format(settings.GOOGLE_VISION_API_KEY)
        responses.add(
            responses.POST,
            url,
            json={'some': 'error'},
            status=400,
            match_querystring=True
        )

        with pytest.raises(AnalysisError):
            google_analyser(self.image_url)


class TestAzureAnalyser(TestCase):
    image_url = 'https://bienal-image-analyser.s3.amazonaws.com/folder/img.jpg?X-Amz-Algorithm=AWS4-HMAC'

    def setUp(self):
        qs = {
            'visualFeatures': 'Categories,Tags,Description,Faces,ImageType,Color,Adult',
            'details': 'Celebrities,Landmarks',
            'language': 'en'
        }
        api_url = 'https://brazilsouth.api.cognitive.microsoft.com/vision/v1.0/analyze'
        self.url = api_url + '?' + urlencode(qs)
        self.headers = {'Ocp-Apim-Subscription-Key': settings.AZURE_VISION_API_KEY}

    @responses.activate
    def test_return_response_if_success(self):
        responses.add(
            responses.POST,
            self.url,
            json=AZURE_ANALYSE_RESPONSE,
            status=200,
            match_querystring=True,
            headers=self.headers,
        )

        data = azure_analyser(self.image_url)
        expected_request = {'url': self.image_url.split('?')[0]}

        json_data = json.loads(responses.calls[0].request.body)
        assert AZURE_ANALYSE_RESPONSE == data['main']
        assert expected_request == json_data

    @responses.activate
    def test_raise_exception_if_any_error(self):
        responses.add(
            responses.POST,
            self.url,
            json={'some': 'error'},
            status=400,
            match_querystring=True,
            headers=self.headers,
        )

        with pytest.raises(AnalysisError):
            azure_analyser(self.image_url)


class TestDeepAIAnalyser(TestCase):
    image_url = 'https://bienal-image-analyser.s3.amazonaws.com/folder/img.jpg?X-Amz-Algorithm=AWS4-HMAC'

    def setUp(self):
        self.url = 'https://api.deepai.org/api/densecap'
        self.headers = {'Api-Key': settings.DEEP_AI_API_KEY}

    @responses.activate
    def test_return_response_if_success(self):
        responses.add(
            responses.POST,
            self.url,
            json=DEEP_API_DENSE_CAP_RESPONSE,
            status=200,
            headers=self.headers,
        )

        data = deep_ai_analyser(self.image_url)
        expected_data = urlencode({'image': self.image_url.split('?')[0]})
        call = responses.calls[0]

        assert expected_data == call.request.body
        assert DEEP_API_DENSE_CAP_RESPONSE == data['DenseCap']

    @responses.activate
    def test_raise_exception_if_any_error(self):
        responses.add(
            responses.POST,
            self.url,
            json={'some': 'error'},
            status=400,
            headers=self.headers,
        )

        with pytest.raises(AnalysisError):
            deep_ai_analyser(self.image_url)
