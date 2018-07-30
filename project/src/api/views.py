from rest_framework.generics import ListAPIView

from src.api.serializers import CollectionSerializer
from src.core.models import Collection


class ListCollectionsEndpoint(ListAPIView):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
