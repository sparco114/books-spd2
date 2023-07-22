from django.test import TestCase
from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg, F

from store.models import Book, UserBookRelation
from store.serializers import BooksSerializer


class BookSerializerTestCase(TestCase):
    def test_ok(self):
        user1 = User.objects.create(username='user1_username',
                                    first_name='Ivan',
                                    last_name='Petrov')
        user2 = User.objects.create(username='user2_username',
                                    first_name='Alex',
                                    last_name='Sidorov')
        user3 = User.objects.create(username='user3_username',
                                    first_name='Ann',
                                    last_name='Stern')
        book1 = Book.objects.create(name='Test book 1', price=111, author_name="Author1", owner=user1)
        book2 = Book.objects.create(name='Test book 22', price=120, author_name="Author2", discount=22)

        user_book_1 = UserBookRelation.objects.create(user=user1, book=book1, like=True, rate=1)
        user_book_2 = UserBookRelation.objects.create(user=user2, book=book1, like=True)
        user_book_3 = UserBookRelation.objects.create(user=user3, book=book1, like=True, rate=5)
        user_book_1.rate = 5
        user_book_1.save()
        user_book_1.rate = 2
        user_book_1.save()
        user_book_2.rate = 5
        user_book_2.save()

        # print('user_book_1====', user_book_1)
        # print('user_book_2====', user_book_2)
        # print('user_book_3====', user_book_3)
        # print('book1.rating====', book1.rating)

        user_book_11 = UserBookRelation.objects.create(user=user1, book=book2, like=True, rate=3)
        user_book_22 = UserBookRelation.objects.create(user=user2, book=book2, like=True, rate=5)
        user_book_33 = UserBookRelation.objects.create(user=user3, book=book2, like=False, rate=5)

        # print('user_book_11====', user_book_11)
        # print('user_book_22====', user_book_22)
        # print('user_book_33====', user_book_33)
        # print('book2.rating====', book2.rating)

        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            # rating=Avg('userbookrelation__rate'), # закомментил, потому что сейчас добавлено поле rating в модель Book, которое считает и сохраняет рейтинг в себе
            price_with_discount=Case(
                When(discount=None, then=F('price')),
                When(discount=0, then=F('price')),
                default=F('price') - (F('price') * F('discount') / 100)),
            owner_name=F('owner__username'),
        ).order_by('id')
        book1.refresh_from_db()
        book2.refresh_from_db()
        data = BooksSerializer(books, many=True).data
        # data = BooksSerializer([book1, book2], many=True).data
        expected_data = [
            {
                'id': book1.id,
                'name': 'Test book 1',
                'price': '111.00',
                'discount': None,
                'price_with_discount': 111,
                'author_name': 'Author1',
                # 'likes_count': 3,
                'annotated_likes': 3,
                'rating': '4.00',
                'owner_name': 'user1_username',
                'readers': [
                    {'first_name': 'Ivan', 'last_name': 'Petrov'},
                    {'first_name': 'Alex', 'last_name': 'Sidorov'},
                    {'first_name': 'Ann', 'last_name': 'Stern'},
                ]
            },
            {
                'id': book2.id,
                'name': 'Test book 22',
                'price': '120.00',
                'discount': 22,
                'price_with_discount': 93,
                'author_name': 'Author2',
                # 'likes_count': 2,
                'annotated_likes': 2,
                'rating': '4.33',
                'owner_name': None,
                'readers': [
                    {'first_name': 'Ivan', 'last_name': 'Petrov'},
                    {'first_name': 'Alex', 'last_name': 'Sidorov'},
                    {'first_name': 'Ann', 'last_name': 'Stern'},
                ]

            }
        ]
        # print('expected_data===', expected_data)
        # print('data============', data)

        self.assertEqual(expected_data, data)
