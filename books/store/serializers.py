from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from store.models import Book, UserBookRelation


class BooksSerializer(ModelSerializer):
    likes_count = serializers.SerializerMethodField()  # первый способ вытащить лайки (метод SerializerMethodField ищет функцию get_<название этого поля>)
    annotated_likes = serializers.IntegerField(read_only=True)  # второй способ вытащить лайки, при этом надо изменить queryset в views.py. read_only=True - нужен чтобы при создании книги это поле не требовалось
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)
    price_with_discount = serializers.IntegerField(read_only=True)

    class Meta:
        model = Book
        # fields = "__all__" # выводить все поля
        fields = ['id', 'name', 'price', 'discount', 'price_with_discount', 'author_name', 'likes_count', 'annotated_likes', 'rating']

    def get_likes_count(self, instance):  # instance - возьмет текущую книгу (объект, который сериализуется)
        return UserBookRelation.objects.filter(book=instance,
                                               like=True).count()  # эта функция для первого способа вытаскивания лайков


class UserBookRelationSerializer(ModelSerializer):
    class Meta:
        model = UserBookRelation
        fields = ['book', 'like', 'in_bookmarks', 'rate', 'bought']
