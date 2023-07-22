from django.contrib.auth.models import User
from django.db.models import Max
from django.test import TestCase
from store.logic import set_rating
from store.models import Book, UserBookRelation


class SetRatingTestCase(TestCase):

    def setUp(self):
        user1 = User.objects.create(username='user1_username',
                                    first_name='Ivan',
                                    last_name='Petrov')
        user2 = User.objects.create(username='user2_username',
                                    first_name='Alex',
                                    last_name='Sidorov')
        user3 = User.objects.create(username='user3_username',
                                    first_name='Ann',
                                    last_name='Stern')
        self.book1 = Book.objects.create(name='Test book 1', price=111, author_name="Author1", owner=user1)

        UserBookRelation.objects.create(user=user1, book=self.book1, like=True, rate=5)
        UserBookRelation.objects.create(user=user2, book=self.book1, like=True, rate=5)
        UserBookRelation.objects.create(user=user3, book=self.book1, like=True, rate=4)

    def test_ok(self):
        # print(set_rating(self.book1))
        set_rating(self.book1)
        # Book.refresh_from_db(self.book1)
        # print('Book====================', Book.objects.filter(id=self.book1.id).aggregate(Max('rating')))
        # print('self.book1.rating=======', self.book1.rating)
        self.book1.refresh_from_db()
        # print('self.book1.rating==R====', self.book1.rating)
        # self.assertEqual(4.666666666666667, self.book1.rating)
        self.assertEqual('4.67', str(self.book1.rating))
