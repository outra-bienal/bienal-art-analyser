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
    ibmwatson = serializers.SerializerMethodField()
    googlecloud = serializers.SerializerMethodField()
    microsoftazure = serializers.SerializerMethodField()
    deepAi = serializers.SerializerMethodField()
    clarifai = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    yolo_image = serializers.SerializerMethodField()
    detectron_image = serializers.SerializerMethodField()
    dense_cap_image = serializers.SerializerMethodField()
    dense_cap_full_image = serializers.SerializerMethodField()

    def _clean_url(self, url):
        return url.split('?')[0]

    def get_amazonRekog(self, analysed_image):
        return analysed_image.recokgnition_result

    def get_ibmwatson(self, analysed_image):
        return analysed_image.ibm_watson_result

    def get_googlecloud(self, analysed_image):
        return analysed_image.google_vision_result

    def get_microsoftazure(self, analysed_image):
        return analysed_image.azure_vision_result

    def get_deepAi(self, analysed_image):
        return analysed_image.deep_ai_result

    def get_clarifai(self, analysed_image):
        return analysed_image.clarifai_result

    def get_image(self, analysed_image):
        img = analysed_image.image
        if img:
            return self._clean_url(img.url)

    def get_yolo_image(self, analysed_image):
        img = analysed_image.yolo_image
        if img:
            return self._clean_url(img.url)

    def get_detectron_image(self, analysed_image):
        img = analysed_image.detectron_image
        if img:
            return self._clean_url(img.url)

    def get_dense_cap_image(self, analysed_image):
        img = analysed_image.dense_cap_image
        if img:
            return self._clean_url(img.url)

    def get_dense_cap_full_image(self, analysed_image):
        img = analysed_image.dense_cap_full_image
        if img:
            return self._clean_url(img.url)

    class Meta:
        model = AnalysedImage
        fields = ['image', 'processed', 'amazonRekog', 'ibmwatson', 'googlecloud', 'microsoftazure', 'yolo_image', 'detectron_image', 'deepAi', 'clarifai', 'dense_cap_image', 'dense_cap_full_image']
