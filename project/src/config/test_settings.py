from .settings import *

TESTING = True

STRING_IF_INVALID = "%%%INVALID_STRING%%%"
TEMPLATES[0]['OPTIONS']['string_if_invalid'] = STRING_IF_INVALID

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR.child('media')
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

AWS_ACCESS_KEY_ID = 'access_key'
AWS_SECRET_ACCESS_KEY = 'secret_access_key'
AWS_STORAGE_BUCKET_NAME = 'bucket'
AWS_S3_HOST = 'host'
AWS_S3_REGION_NAME = 'region'

IBM_IAM_API_KEY = 'ibm_api_key'
