from rest_framework.generics import ListAPIView, RetrieveAPIView

from src.api.serializers import CollectionSerializer, CollectionDetailSerializer, AnalysedImageSerializer
from src.core.models import Collection, AnalysedImage


class ListCollectionsEndpoint(ListAPIView):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer


class DetailCollectionEndpoint(RetrieveAPIView):
    queryset = Collection.objects.all()
    serializer_class = CollectionDetailSerializer


class DetailAnalysedImageEndpoint(RetrieveAPIView):
    serializer_class = AnalysedImageSerializer

    def get_queryset(self, *args, **kwargs):
        return AnalysedImage.objects.filter(collection__pk=self.kwargs['col_pk'])
