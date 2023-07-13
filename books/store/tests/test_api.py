import json

from django.urls import reverse
from rest_framework.test import APITestCase
import rest_framework.status as status
from django.contrib.auth.models import User
from rest_framework.exceptions import ErrorDetail

from store.models import Book, UserBookRelation
from store.serializers import BooksSerializer


class BooksApiTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(username='test_username')
        self.book1 = Book.objects.create(name='Test book 1 author 1', price=25, author_name='author 5', owner=self.user)
        self.book2 = Book.objects.create(name='Test book 2', price=55, author_name='author 1')
        self.book3 = Book.objects.create(name='Test book 3', price=55, author_name='author 2')

    def test_get(self):
        url = reverse('book-list')  # list - чтоб создалась верная ссылка
        # print(url)
        response = self.client.get(url)
        serializer_data = BooksSerializer([self.book1, self.book2, self.book3],
                                          many=True).data  # если один объект, тогда можно указать без many и не списком
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

    def test_create(self):
        self.assertEqual(3,
                         Book.objects.all().count())  # берем количество изначально созданных книг в методе setUp этого класса
        url = reverse('book-list')
        data = {
            "name": "Crypto",
            "price": "22.00",
            "author_name": "Binxxxxxxance",
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(4, Book.objects.all().count())
        self.assertEqual('Crypto', Book.objects.all()[3].name)
        # print('==========', Book.objects.last().owner)

    def test_update(self):
        url = reverse('book-detail', args=(
            self.book1.id,))  # вместо list нужно указать так, если хотим не весь список, а выборочно в соответствии с args
        data = {
            "name": self.book1.name,
            "price": '1000.00',
            "author_name": self.book1.author_name,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        Book.refresh_from_db(
            self.book1)  # такое обновление нужно, потому что он изменился там в базе, но не обновился в рамках теста. Такая проблема может быть если обращаться здесь через self.book1. А если образаться через базу (Book.objects.all()[0].price), тогда проблемы не будет, но не всегда знаешь порядковый номер объекта в базе, т.е. в нашем случае [2]

        self.assertEqual(1000.00, self.book1.price)

        # self.assertEqual(1000.00, Book.objects.all()[2].price) # в этом случае тянет обновленную инфу из базы, но тут надо угадывать порядковый номер

    def test_update_not_owner(self):
        self.user2 = User.objects.create_user(username='test_username2')
        url = reverse('book-detail', args=(
            self.book1.id,))
        data = {
            "name": self.book1.name,
            "price": '1000.00',
            "author_name": self.book1.author_name,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        response = self.client.put(url, data=json_data, content_type='application/json')
        Book.refresh_from_db(self.book1)
        self.assertEqual(25, self.book1.price)
        # print(response.data)
        self.assertEqual({'detail': ErrorDetail(string='You do not have permission to perform this action.',
                                                code='permission_denied')}, response.data)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_update_not_owner_but_staff(self):
        self.user2 = User.objects.create_user(username='test_username2', is_staff=True)
        url = reverse('book-detail', args=(
            self.book1.id,))
        data = {
            "name": self.book1.name,
            "price": '1000.00',
            "author_name": self.book1.author_name,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        response = self.client.put(url, data=json_data, content_type='application/json')
        Book.refresh_from_db(self.book1)
        self.assertEqual(1000, self.book1.price)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_delete(self):
        self.assertEqual(3, Book.objects.all().count())
        url = reverse('book-detail', args=(self.book1.id,))
        self.client.force_login(self.user)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

        self.assertEqual(2, Book.objects.all().count())
        self.assertEqual([self.book2, self.book3], [i for i in Book.objects.all()])

    def test_delete_not_owner(self):
        self.user2 = User.objects.create_user(username='test_username2')
        self.assertEqual(3, Book.objects.all().count())
        url = reverse('book-detail', args=(self.book1.id,))
        self.client.force_login(self.user2)
        response = self.client.delete(url)
        # print(response.data)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual(3, Book.objects.all().count())
        self.assertEqual([self.book1, self.book2, self.book3], [i for i in Book.objects.all()])
        self.assertEqual({'detail': ErrorDetail(string='You do not have permission to perform this action.',
                                                code='permission_denied')}, response.data)

    def test_get_one_object(self):
        url = reverse('book-detail', args=(self.book1.id,))
        self.client.force_login(self.user)
        response = self.client.get(url)
        serializer_data = BooksSerializer(self.book1).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)


class BooksRelationTestCase(APITestCase):

    def setUp(self):
        self.user1 = User.objects.create(username='test_username1')
        self.user2 = User.objects.create(username='test_username2')
        self.book1 = Book.objects.create(name='Test book 1 author 1', price=25, author_name='author 5',
                                         owner=self.user1)
        self.book2 = Book.objects.create(name='Test book 2', price=55, author_name='author 1')

    def test_like(self):
        url = reverse('userbookrelation-detail', args=(self.book1.id,))

        self.client.force_login(user=self.user1)

        data = {
            'like': True
        }
        json_data = json.dumps(data)
        response = self.client.patch(path=url,
                                     data=json_data,
                                     content_type='application/json')  # patch - можно передать одно поле, не обязательно передаветь данные всех полей при изменении объекта
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        # Book.refresh_from_db(self.book1)      # можно так
        self.book1.refresh_from_db()            # а можно так
        relation = UserBookRelation.objects.get(user=self.user1, book=self.book1)
        self.assertTrue(relation.like)

        data = {
            'in_bookmarks': True
        }
        json_data = json.dumps(data)
        response = self.client.patch(path=url,
                                     data=json_data,
                                     content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user1, book=self.book1)
        self.assertTrue(relation.in_bookmarks)

    def test_rate(self):
        url = reverse('userbookrelation-detail', args=(self.book1.id,))

        self.client.force_login(user=self.user1)

        data = {
            'rate': 1
        }
        json_data = json.dumps(data)
        response = self.client.patch(path=url,
                                     data=json_data,
                                     content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book1.refresh_from_db()
        relation = UserBookRelation.objects.get(user=self.user1, book=self.book1)
        print('relation.rate', relation)
        self.assertEqual(1, relation.rate)

    def test_rate_wrong(self):
        url = reverse('userbookrelation-detail', args=(self.book1.id,))

        self.client.force_login(user=self.user1)

        data = {
            'rate': 6
        }
        json_data = json.dumps(data)
        response = self.client.patch(path=url,
                                     data=json_data,
                                     content_type='application/json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code, response.data) # третьим аргументом можно выводить ошибку, которую нам вернет ответ
        err = {'rate': [ErrorDetail(string='"6" is not a valid choice.', code='invalid_choice')]}
        self.assertEqual(err, response.data)
