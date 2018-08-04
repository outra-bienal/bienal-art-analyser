from urllib.parse import urlparse, urlencode

import json
import boto3
import requests
from watson_developer_cloud import VisualRecognitionV3

from django.conf import settings


def aws_analyser(image_url):
    client = boto3.client(
        'rekognition',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )

    image = {
        'S3Object': {
            'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
            'Name': urlparse(image_url).path[1:],
        }
    }
    try:
        return {
            'labels': client.detect_labels(Image=image),
            'faces': client.detect_faces(Image=image),
            'celebs': client.recognize_celebrities(Image=image)
        }
    except Exception as e:
        print(e)
        return None


def ibm_analyser(image_url):
    client = VisualRecognitionV3(
        settings.IBM_WATSON_VISUAL_RECOG_VERSION,
        iam_api_key=settings.IBM_IAM_API_KEY,
    )

    clean_url = image_url.split('?')[0]
    params = json.dumps({'url': clean_url})
    try:
        return {
            'main': client.classify(url=clean_url)['images'][0],
            'faces': client.detect_faces(parameters=params)['images'][0],
        }
    except Exception as e:
        print(e)
        return None


def google_analyser(image_url):
    image_url = image_url.split('?')[0]
    qs = {'key': settings.GOOGLE_VISION_API_KEY}
    api_url = 'https://vision.googleapis.com/v1/images:annotate'
    request = {
        "image": {"source": {"imageUri": image_url}},
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

    response = requests.post(api_url, json={'requests': [request]}, params=qs)
    if response.ok:
        return response.json()['responses'][0]


def azure_analyser(image_url):
    url = 'https://brazilsouth.api.cognitive.microsoft.com/vision/v1.0/analyze'
    qs = {
        'visualFeatures': 'Categories,Tags,Description,Faces,ImageType,Color,Adult',
        'details': 'Celebrities,Landmarks',
        'language': 'en'
    }
    headers = {'Ocp-Apim-Subscription-Key': settings.AZURE_VISION_API_KEY}

    image_url = image_url.split('?')[0]
    response = requests.post(url, headers=headers, params=qs, json={'url': image_url})

    if response.ok:
        return {'main': response.json()}
