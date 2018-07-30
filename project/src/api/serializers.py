from rest_framework import serializers

from src.core.models import Collection


class CollectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Collection
        fields = '__all__'


class CollectionDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Collection
        fields = '__all__'
