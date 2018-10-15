from django.views.decorators.cache import cache_page
from django.conf.urls import url
from django.conf import settings
from django.urls import re_path, path

from src.api.views import ListCollectionsEndpoint, DetailCollectionEndpoint, DetailAnalysedImageEndpoint


app_name = 'api'
urlpatterns = [
    re_path(r'^collection/$', cache_page(settings.CACHE_DEFAULT_TIMEOUT, key_prefix="collection_list")(ListCollectionsEndpoint.as_view()), name='list_collections'),
    path('collection/<int:pk>/', cache_page(settings.CACHE_DEFAULT_TIMEOUT, key_prefix="collection_detail")(DetailCollectionEndpoint.as_view()), name='collection_detail'),
    path('collection/<int:col_pk>/image/<int:pk>/', cache_page(settings.CACHE_DEFAULT_TIMEOUT, key_prefix="image_detail")(DetailAnalysedImageEndpoint.as_view()), name='image_detail'),
]
