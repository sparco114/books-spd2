from django.test import TestCase

from store.models import Book
from store.serializers import BooksSerializer


class BookerializerTestCase(TestCase):
    def test_ok(self):
        book1 = Book.objects.create(name='Test book 1', price=111.00)
        book2 = Book.objects.create(name='Test book 22', price=120.00)
        data = BooksSerializer([book1, book2], many=True).data
        expected_data = [
            {
                'id': book1.id,
                'name': 'Test book 1',
                'price': '111.00',
            },
            {
                'id': book2.id,
                'name': 'Test book 22',
                'price': '120.00',
            }
        ]
        self.assertEqual(expected_data, data)
