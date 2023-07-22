from django.db.models import When, Case, Count, Avg, F
from rest_framework.mixins import UpdateModelMixin
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.shortcuts import render

from store.models import Book, UserBookRelation
from store.permissions import IsOwnerOrStaffOrReadOnly
from store.serializers import BooksSerializer, UserBookRelationSerializer


class BookViewSet(ModelViewSet):
    # queryset = Book.objects.all() # стандартный сет (если без annotane в сериалайзере)

    # если используем для подтягивания лайков к книге annotate в сериалайзере, то нужно указывать так:
    queryset = Book.objects.all().annotate(
        annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
        # rating=Avg('userbookrelation__rate'), # каждый раз высчитывает в среднюю величину. Можно добавить поле в модель Book, чтобы оно хранилось и хешировалось при обновлении количества лайков. При добавлении такого поля в Book нужно удалить отсюда.
        price_with_discount=Case(
            When(discount=None, then=F('price')),
            When(discount=0, then=F('price')),
            default=F('price') - (F('price') * F('discount') / 100)),
        owner_name=F('owner__username'), # можно обратиться к полю owner в Book и оттуда взять
        # owner_name=F('userbookrelation__user__username'), # а можно обратиться к модели userbookrelation и оттуда взять

        ).prefetch_related('readers').order_by( # можно аннотировать поле owner_name внутри annotate, тогда будет тянуть в запросе только его, а можно указать select_related как ниже сделано, тогда будет тянуть все поля из User.

        # ).select_related('owner').prefetch_related('readers').order_by(
        'id')  # select_related - по полю owner выбирает один объект, связанный с книгой (то есть раотает для foreignKey) связывает таблицы запроса, чтоб не делать несколько запросов в базу отдельно для модели книги и модели UserBookRelation
    # prefetch_related - по полю readers выбирает ВСЕ объекты, связанные с книгой.
    # можно указать так "order_by(F('discount').desc(nulls_last=True), 'id')" чтобы сортировало сначала по discount, и значения null выставляет в конец, а потом сортировало это по id. Но при применении фильтра сортировки в гет запросе это не работает, для этого нужно переопределить функцию get_ordering в классе OrderingFilter, который указан здесь в filter_backends

    serializer_class = BooksSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # permission_classes = [IsAuthenticated]
    # permission_classes = [IsAuthenticatedOrReadOnly] # стандартный класс, дает читать чтолько аутентифицированным
    permission_classes = [
        IsOwnerOrStaffOrReadOnly]  # создали кастомный класс, который проверяет является ли клиент создателем объекта
    filterset_fields = ['id', 'price', 'name']
    search_fields = ['author_name', 'name']
    ordering_fields = ['price', 'name', 'discount']

    def perform_create(self, serializer):
        serializer.validated_data['owner'] = self.request.user
        serializer.save()


class UserBookRelationView(UpdateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = UserBookRelation.objects.all()
    serializer_class = UserBookRelationSerializer
    lookup_field = 'bookk'

    def get_object(self):
        obj, _ = UserBookRelation.objects.get_or_create(user=self.request.user,
                                                        book_id=self.kwargs['bookk'],
                                                        )  # метод get_or_create возвращает объект и статус - найден он или создан, поэтому переменной '_' присвоится этот статус, но он нам не важен
        # print('============b', self.kwargs)
        # print('============u', self.request.user)
        # print('============o', obj)
        return obj


def auth(request):
    return render(request=request, template_name='oauth.html')
