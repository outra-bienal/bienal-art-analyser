from .settings import *

TESTING = True

STRING_IF_INVALID = "%%%INVALID_STRING%%%"
TEMPLATES[0]['OPTIONS']['string_if_invalid'] = STRING_IF_INVALID

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR.child('media')
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
