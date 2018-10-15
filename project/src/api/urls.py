from django.conf.urls import url
from django.urls import re_path, path

from src.api.views import ListCollectionsEndpoint, DetailCollectionEndpoint, DetailAnalysedImageEndpoint


app_name = 'api'
urlpatterns = [
    re_path(r'^collection/$', ListCollectionsEndpoint.as_view(), name='list_collections'),
    path('collection/<int:pk>/', DetailCollectionEndpoint.as_view(), name='collection_detail'),
    path('collection/<int:col_pk>/image/<int:pk>/', DetailAnalysedImageEndpoint.as_view(), name='image_detail'),
]
