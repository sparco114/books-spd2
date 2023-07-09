from django.urls import reverse
from rest_framework.test import APITestCase
import rest_framework.status as status

from store.models import Book
from store.serializers import BooksSerializer


class BooksApiTestCase(APITestCase):

    def test_get(self):
        book1 = Book.objects.create(name='Test book 1', price=111.00)
        book2 = Book.objects.create(name='Test book 22', price=120.00)
        url = reverse('book-list')      # list - чтоб создалась верная ссылка
        # print(url)
        response = self.client.get(url)
        serializer_data = BooksSerializer([book1, book2], many=True).data       #если один объект, тогда можно указать без many и не списком
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)
        # print(response.data)
