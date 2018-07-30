from model_mommy import mommy
from rest_framework.test import APITestCase

from django.urls import reverse

from src.api.serializers import CollectionDetailSerializer


def formated_date(obj):
    if not obj:
        return obj
    isoformat = obj.isoformat()
    return isoformat.split('+')[0]


class ListCollectionsTests(APITestCase):

    def setUp(self):
        self.collection = mommy.make('core.Collection')
        self.url = reverse('api:list_collections')

    def test_serialize_collections(self):
        response = self.client.get(self.url)
        expected = [{
            'title': self.collection.title,
            'date': formated_date(self.collection.date),
            'id': self.collection.id,
            'detail_url': reverse('api:list_collections', args=[self.collection.id]),
            'processed': self.collection.processed,
        }]

        assert 200 == response.status_code
        assert expected == response.json()


class DetailCollectionTests(APITestCase):

    def setUp(self):
        self.collection = mommy.make('core.Collection')
        self.url = reverse('api:list_collections', args=[self.collection.id])

    def test_serialize_collection(self):
        response = self.client.get(self.url)
        expected = CollectionDetailSerializer(instance=self.collection).data

        assert 200 == response.status_code
        assert expected == response.json()
