import logging
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from .models import Articulo, Categoria, Proveedor
from .serializers import ArticuloSerializer, CategoriaSerializer, ProveedorSerializer
from django.db.models import Q

logger = logging.getLogger(__name__)

class ArticuloViewSet(viewsets.ModelViewSet):
    serializer_class = ArticuloSerializer
    # permission_classes = [permissions.IsAuthenticated]  # Comentado para desarrollo
    pagination_class = PageNumberPagination
    pagination_class.page_size = 10

    def get_queryset(self):
        queryset = Articulo.objects.all()
        search = self.request.query_params.get('search', None)
        stock_bajo = self.request.query_params.get('stock_bajo', None)

        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) | Q(categoria__nombre__icontains=search)
            )
        if stock_bajo and stock_bajo.lower() == 'true':
            queryset = queryset.filter(stock__lte=5)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page_size = int(self.request.query_params.get('page_size', 10))
        self.pagination_class.page_size = page_size
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        logger.debug(f"Datos recibidos: {request.data}")
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Errores de validación: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    # permission_classes = [permissions.IsAuthenticated]  # Comentado para desarrollo
    pagination_class = PageNumberPagination

class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    # permission_classes = [permissions.IsAuthenticated]  # Comentado para desarrollo
    pagination_class = PageNumberPagination