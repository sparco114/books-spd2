from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from store.models import Book, UserBookRelation

class BookReaderSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')

class BooksSerializer(ModelSerializer):
    # likes_count = serializers.SerializerMethodField()  # первый способ вытащить лайки (метод SerializerMethodField ищет функцию get_<название этого поля>)
    annotated_likes = serializers.IntegerField(read_only=True)  # второй способ вытащить лайки, при этом надо изменить queryset в views.py. read_only=True - нужен чтобы при создании книги это поле не требовалось
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)
    price_with_discount = serializers.IntegerField(read_only=True)

    # owner_name = serializers.CharField(source='owner.username', default='-', read_only=True) # обращаемся в Book, там есть поле owner из него берем что нужно. Этот вариант, если в view.py в queryset добавляем .select_related('owner'), если без него, то вытаскиваем поле owner_name через annotate и строка будет такой:

    owner_name = serializers.CharField(read_only=True) # в случае если вытаскиваем поле owner_name через annotate

    readers = BookReaderSerializer(many=True, read_only=True) # название должно соответствовать названию поля в Book, а если хотим поменять, то можно сделать так:
    # readers_asd = BookReaderSerializer(many=True, source='readers')


    class Meta:
        model = Book
        # fields = "__all__" # выводить все поля
        fields = ['id', 'name', 'price', 'discount', 'price_with_discount', 'author_name',
                  # 'likes_count',
                  'annotated_likes',
                  'rating',
                  'owner_name',
                  'readers'
                  ]

    # def get_likes_count(self, instance):  # instance - возьмет текущую книгу (объект, который сериализуется)
    #     return UserBookRelation.objects.filter(book=instance,
    #                                            like=True).count()  # эта функция для первого способа вытаскивания лайков. НО она создает отдельный запрос в базу для каждой книги, это видно в django debug tools. Поэтому проще через annotation в этом случае


class UserBookRelationSerializer(ModelSerializer):
    class Meta:
        model = UserBookRelation
        fields = ['book', 'like', 'in_bookmarks', 'rate', 'bought']
