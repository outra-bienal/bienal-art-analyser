from model_mommy import mommy

from django.test import TestCase
from django.urls import reverse

from .utils import formated_date
from src.api.serializers import CollectionSerializer, AnalysedImageSerializer, CollectionDetailSerializer
from src.core.models import AnalysedImage, Collection


class AnalysedImageSerializerTests(TestCase):

    def test_serialize_analysed_image(self):
        analysed_image = mommy.make(
            AnalysedImage,
            recokgnition_result={'aws': 'bar'},
            ibm_watson_result={'ibm': 'data'},
            google_vision_result={'google': 'data'},
            azure_vision_result={'azure': 'data'},
            deep_ai_result={'deep_ai': 'data'},
            clarifai_result={'clarifai': 'data'},
            _create_files=True,
            _fill_optional=True
        )

        serializer = AnalysedImageSerializer(instance=analysed_image)
        expected = {
            'pk': analysed_image.pk,
            'detail_url': reverse('api:image_detail', args=[analysed_image.collection_id, analysed_image.pk]),
            'image': analysed_image.image.url,
            'amazonRekog': {'aws': 'bar'},
            'ibmwatson': {'ibm': 'data'},
            'googlecloud': {'google': 'data'},
            'microsoftazure': {'azure': 'data'},
            'deepAi': {'deep_ai': 'data'},
            'clarifai': {'clarifai': 'data'},
            'processed': analysed_image.processed,
            'yolo_image': analysed_image.yolo_image.url,
            'detectron_image': analysed_image.detectron_image.url,
            'dense_cap_image': analysed_image.dense_cap_image.url,
            'dense_cap_full_image': analysed_image.dense_cap_full_image.url,
        }

        assert expected == serializer.data


class CollectionDetailSerializerTests(TestCase):

    def test_collection_detail_serializer(self):
        collection = mommy.make(Collection)
        analysed_images = mommy.make(AnalysedImage, collection=collection, _quantity=3)
        analysed_images = collection.analysed_images.all()

        serializer = CollectionDetailSerializer(instance=collection)
        expected = {
            'title': collection.title,
            'date': formated_date(collection.date),
            'id': collection.id,
            'processed': collection.processed,
            'images': AnalysedImageSerializer(analysed_images, many=True).data
        }

        assert expected == serializer.data
