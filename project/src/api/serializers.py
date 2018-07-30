from rest_framework import serializers

from django.urls import reverse

from src.core.models import Collection


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

    class Meta:
        model = Collection
        fields = '__all__'
