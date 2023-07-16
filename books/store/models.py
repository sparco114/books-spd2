from django.db import models
from django.contrib.auth.models import User


class Book(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    author_name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='my_books')
    readers = models.ManyToManyField(User, through='UserBookRelation', related_name='books')

    def __str__(self):
        return f'ID {self.id}: {self.name}'


class UserBookRelation(models.Model):
    RATE_CHOICES = (
        (1, 'Ok'),
        (2, 'Fine'),
        (3, 'Good'),
        (4, 'Amazing'),
        (5, 'Incredible'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    like = models.BooleanField(default=False)
    in_bookmarks = models.BooleanField(default=False)
    rate = models.PositiveSmallIntegerField(choices=RATE_CHOICES, null=True)
    bought = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username}, ' \
               f'{self.book.name}, ' \
               f'RATE: {self.rate}, ' \
               f'like: {self.like}, ' \
               f'in_bookmarks: {self.in_bookmarks}, ' \
               f'bought: {self.bought}'
