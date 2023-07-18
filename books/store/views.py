from django.db.models import When, Case, Count
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
    ).order_by('id')

    serializer_class = BooksSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # permission_classes = [IsAuthenticated]
    # permission_classes = [IsAuthenticatedOrReadOnly] # стандартный класс, дает читать чтолько аутентифицированным
    permission_classes = [
        IsOwnerOrStaffOrReadOnly]  # создали кастомный класс, который проверяет является ли клиент создателем объекта
    filterset_fields = ['price', 'name']
    search_fields = ['author_name', 'name']
    ordering_fields = ['price', 'name']

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
                                                        ) # метод get_or_create возвращает объект и статус - найден он или создан, поэтому переменной '_' присвоится этот статус, но он нам не важен
        # print('============b', self.kwargs)
        # print('============u', self.request.user)
        # print('============o', obj)
        return obj


def auth(request):
    return render(request=request, template_name='oauth.html')
