from django.urls import reverse
from rest_framework.test import APITestCase
import rest_framework.status as status

from store.models import Book
from store.serializers import BooksSerializer


class BooksApiTestCase(APITestCase):

    def setUp(self):
        self.book1 = Book.objects.create(name='Test book 1 author 1', price=25, author_name='author 5')
        self.book2 = Book.objects.create(name='Test book 2', price=55, author_name='author 1')
        self.book3 = Book.objects.create(name='Test book 3', price=55, author_name='author 2')

    def test_get(self):
        url = reverse('book-list')      # list - чтоб создалась верная ссылка
        # print(url)
        response = self.client.get(url)
        serializer_data = BooksSerializer([self.book1, self.book2, self.book3], many=True).data       #если один объект, тогда можно указать без many и не списком
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)
        # print(response.data)

    def test_get_filter(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'price': 55})
        serializer_data = BooksSerializer([self.book2, self.book3], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_search(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'search': 'author 1'})
        serializer_data = BooksSerializer([self.book1, self.book2], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_ordering(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'ordering': '-name'})
        serializer_data = BooksSerializer([self.book3, self.book2, self.book1], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)
