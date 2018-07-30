from rest_framework import serializers

from django.urls import reverse

from src.core.models import Collection, AnalysedImage


class CollectionSerializer(serializers.ModelSerializer):
    detail_url = serializers.SerializerMethodField()
    processed = serializers.SerializerMethodField()

    def get_detail_url(self, collection):
        return reverse('api:list_collections', args=[collection.id])

    def get_processed(self, collection):
        return collection.processed

    class Meta:
        model = Collection
        fields = '__all__'


class CollectionDetailSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()

    def get_images(self, collection):
        return AnalysedImageSerializer(collection.analysed_images.all(), many=True).data

    class Meta:
        model = Collection
        fields = ['id', 'title', 'date', 'processed', 'images']


class AnalysedImageSerializer(serializers.ModelSerializer):
    amazonRekog = serializers.SerializerMethodField()

    def get_amazonRekog(self, analysed_image):
        return analysed_image.recokgnition_result

    class Meta:
        model = AnalysedImage
        fields = ['image', 'processed', 'amazonRekog']
