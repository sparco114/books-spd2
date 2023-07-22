from django.db.models import Avg

from store.models import UserBookRelation


def set_rating(book):

    rating_res = UserBookRelation.objects.filter(book=book).aggregate(book_rating_count=Avg('rate')).get('book_rating_count') # aggregate возвращает словарь, а через get обращаемся к ключу словаря, можно просто через [book_rating_count]
    book.rating = rating_res
    # print('book.rating===================/////', book.rating, book.name)
    book.save()
