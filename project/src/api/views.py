from rest_framework.generics import ListAPIView, RetrieveAPIView

from src.api.serializers import CollectionSerializer, CollectionDetailSerializer
from src.core.models import Collection


class ListCollectionsEndpoint(ListAPIView):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer


class DetailCollectionEndpoint(RetrieveAPIView):
    queryset = Collection.objects.all()
    serializer_class = CollectionDetailSerializer
