from django.db import models
from django.contrib.auth.models import User



class Book(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    author_name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='my_books')
    readers = models.ManyToManyField(User, through='UserBookRelation', related_name='books')
    discount = models.IntegerField(blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=None, null=True)

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


    def __init__(self, *args, **kwargs):
        super(UserBookRelation, self).__init__(*args, **kwargs)
        self.old_rate = self.rate # чтобы получить старое значение rate, создаем переменную на уровне родительского класса и в нее сохраняем значение rate


    def save(self, *args, **kwargs): # пишем свой метод save (который есть в ролительском классе Model), который вызывается при сохранении модели, и добавляем туда свою функцию set_rating, которая будет пересчитывать рейтинг, при каждом сохранении UserBookRelation.


        from store.logic import set_rating # делаем локальный импорт, потому что мы вызываем внутри этого класса функцию set_rating, в которой используется сам этот класс, то есть получается замкнутый круг, и питон так не отрабатывает

        creating1 = not self.pk # если такая связь еще не создана, то не будет и pk, проверяем это, чтобы добавить в условие if ниже. Это нужно чтоб запустить пересчет рейтинга в случае, когда рейтинг не только изменился, но и в случае когда создалась новая связь в которой сразу указан рейтинг. not - чтобы в переменной creating1 создалось что-то, если рейтинга еще нет.
        super().save(*args, **kwargs) #  но делаем так, чтоб метод save  не перезаписался в родительском классе Model

        # print('old_rate===///', self.book, '=', self.old_rate, '--', self.user)
        # print('new_rate===///', self.book, '=', self.rate, '--', self.user)

        # new_rating = self.rate # можно не рефрешить, потому что self всегда актуальное с базой
        if self.rate != self.old_rate or creating1:
            set_rating(self.book)


