from model_mommy import mommy
from rest_framework.test import APITestCase

from django.urls import reverse

from .utils import formated_date
from src.api.serializers import CollectionDetailSerializer


class ListCollectionsTests(APITestCase):

    def setUp(self):
        self.collection = mommy.make('core.Collection')
        self.url = reverse('api:list_collections')

    def test_serialize_collections(self):
        mommy.make('core.Collection', public=False)
        response = self.client.get(self.url)
        expected = [{
            'title': self.collection.title,
            'date': formated_date(self.collection.date),
            'id': self.collection.id,
            'detail_url': reverse('api:collection_detail', args=[self.collection.id]),
            'processed': self.collection.processed,
        }]

        assert 200 == response.status_code
        assert expected == response.json()


class DetailCollectionTests(APITestCase):

    def setUp(self):
        self.collection = mommy.make('core.Collection')
        self.url = reverse('api:collection_detail', args=[self.collection.id])

    def test_serialize_collection(self):
        response = self.client.get(self.url)
        expected = CollectionDetailSerializer(instance=self.collection).data

        assert 200 == response.status_code
        assert expected == response.json()

    def test_404_if_not_public(self):
        self.collection.public = False
        self.collection.save()

        response = self.client.get(self.url)

        assert 404 == response.status_code
