from django.conf.urls import url
from django.urls import re_path

from src.api.views import ListCollectionsEndpoint


app_name = 'api'
urlpatterns = [
    re_path(r'^collection/$', ListCollectionsEndpoint.as_view(), name='list_collections'),
]
