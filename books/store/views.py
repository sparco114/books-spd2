from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render

from store.models import Book
from store.serializers import BooksSerializer


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BooksSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    permission_classes = [IsAuthenticated]
    filterset_fields = ['price', 'name']
    search_fields = ['author_name', 'name']
    ordering_fields = ['price', 'name']


def auth(request):
    return render(request=request, template_name='oauth.html')