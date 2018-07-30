import boto3
from urllib.parse import urlparse

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
